"""Karpathy's baby GPT, pointed at a DFA -- Chapter 6's laboratory.

A transformer with context length `k` over a vocabulary of size `v` IS a
finite-state machine with `v**k` states: its state is exactly the last `k`
tokens, and that is fixed by the architecture before any training happens.
So "can it learn this DFA?" has an automata-theoretic answer, and this
module lets you check both halves of it.

    from jove.GPTLab import *
    acc, seq = corpus(D)            # accepted strings, joined by an END token
    g = train(seq, k=3)             # Karpathy's GPT, a few seconds
    report(g, D, k=3)               # P(END) per window vs what D accepts

THE END TOKEN EARNS ITS PLACE.  A next-symbol model can only express
constraints on CONTINUATIONS.  Acceptance is a constraint on where you may
STOP, so without a token meaning "the string ends here" a generator cannot
represent a language like parity at all -- every binary string is a prefix
of an accepted one.  With END, P(END | window) is exactly the model's
opinion about acceptance, and can be compared against the DFA directly.

    k_local(D, k)                   # can ANY context-k model learn D?

k_local needs no torch and no training.  It asks whether the minimal DFA's
state is a function of the last k symbols -- Myhill-Nerode run against a
window.  If two prefixes sharing their last k symbols land in different
states of the MINIMAL machine then those states are distinguishable, so the
model must answer differently on inputs it cannot tell apart.  No amount of
data fixes that, and the result is not about SIZE: parity has a two-state
minimal DFA and is k-local for no k at all.

The model is Andrej Karpathy's minimal GPT, unchanged apart from deferring
its torch import.  torch is preinstalled on Colab; elsewhere this module
says so rather than failing obscurely.
"""

import itertools
import math

__all__ = ['END', 'corpus', 'train', 'dist', 'report', 'k_local',
           'colliding_prefixes', 'torch_available', 'windows_seen',
           'plot_chain', 'plot_loss']

END = 2                      # the third token: "the string ends here"

_T = {}                      # torch, nn, F and the model classes, once loaded


def torch_available():
    """(ok, reason).  torch is preinstalled on Colab; elsewhere it may not be."""
    try:
        _load()
        return True, ''
    except Exception as e:
        return False, '%s: %s' % (type(e).__name__, e)


def _load():
    """Import torch and build the model classes, on first use."""
    if _T:
        return _T
    import math
    from dataclasses import dataclass
    import torch
    import torch.nn as nn
    from torch.nn import functional as F
    ns = dict(math=math, dataclass=dataclass, torch=torch, nn=nn, F=F)
    exec(_GPT_SRC, ns)
    _T.update(torch=torch, nn=nn, F=F, GPT=ns['GPT'],
              GPTConfig=ns['GPTConfig'])
    return _T


def __getattr__(name):
    """GPT and GPTConfig exist only once torch has been imported."""
    if name in ('GPT', 'GPTConfig'):
        return _load()[name]
    raise AttributeError(name)


_GPT_SRC = r'''class CausalSelfAttention(nn.Module):

    def __init__(self, config):
        super().__init__()
        assert config.n_embd % config.n_head == 0
        # key, query, value projections for all heads, but in a batch
        self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd, bias=config.bias)
        # output projection
        self.c_proj = nn.Linear(config.n_embd, config.n_embd, bias=config.bias)
        # regularization
        self.n_head = config.n_head
        self.n_embd = config.n_embd
        self.register_buffer("bias", torch.tril(torch.ones(config.block_size, config.block_size))
                                    .view(1, 1, config.block_size, config.block_size))

    def forward(self, x):
        B, T, C = x.size() # batch size, sequence length, embedding dimensionality (n_embd)

        # calculate query, key, values for all heads in batch and move head forward to be the batch dim
        q, k ,v  = self.c_attn(x).split(self.n_embd, dim=2)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)

        # manual implementation of attention
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        y = att @ v # (B, nh, T, T) x (B, nh, T, hs) -> (B, nh, T, hs)
        y = y.transpose(1, 2).contiguous().view(B, T, C) # re-assemble all head outputs side by side

        # output projection
        y = self.c_proj(y)
        return y

class MLP(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.c_fc    = nn.Linear(config.n_embd, 4 * config.n_embd, bias=config.bias)
        self.c_proj  = nn.Linear(4 * config.n_embd, config.n_embd, bias=config.bias)
        self.nonlin = nn.GELU()

    def forward(self, x):
        x = self.c_fc(x)
        x = self.nonlin(x)
        x = self.c_proj(x)
        return x

class Block(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.n_embd)
        self.mlp = MLP(config)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x

@dataclass
class GPTConfig:
    # these are default GPT-2 hyperparameters
    block_size: int = 1024
    vocab_size: int = 50304
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    bias: bool = False

class GPT(nn.Module):

    def __init__(self, config):
        super().__init__()
        assert config.vocab_size is not None
        assert config.block_size is not None
        self.config = config

        self.transformer = nn.ModuleDict(dict(
            wte = nn.Embedding(config.vocab_size, config.n_embd),
            wpe = nn.Embedding(config.block_size, config.n_embd),
            h = nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
            ln_f = nn.LayerNorm(config.n_embd),
        ))
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        self.transformer.wte.weight = self.lm_head.weight # https://paperswithcode.com/method/weight-tying

        # init all weights
        self.apply(self._init_weights)
        # apply special scaled init to the residual projections, per GPT-2 paper
        for pn, p in self.named_parameters():
            if pn.endswith('c_proj.weight'):
                torch.nn.init.normal_(p, mean=0.0, std=0.02/math.sqrt(2 * config.n_layer))

        # report number of parameters
        print("number of parameters: %d" % (sum(p.nelement() for p in self.parameters()),))

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx):
        device = idx.device
        b, t = idx.size()
        assert t <= self.config.block_size, f"Cannot forward sequence of length {t}, block size is only {self.config.block_size}"
        pos = torch.arange(0, t, dtype=torch.long, device=device).unsqueeze(0) # shape (1, t)

        # forward the GPT model itself
        tok_emb = self.transformer.wte(idx) # token embeddings of shape (b, t, n_embd)
        pos_emb = self.transformer.wpe(pos) # position embeddings of shape (1, t, n_embd)
        x = tok_emb + pos_emb
        for block in self.transformer.h:
            x = block(x)
        x = self.transformer.ln_f(x)
        logits = self.lm_head(x[:, -1, :]) # note: only returning logits at the last time step (-1), output is 2D (b, vocab_size)
        return logits'''


# ---- the corpus ---------------------------------------------------------

def corpus(D, upto=400, alphabet=('0', '1')):
    """Accepted strings, each terminated by END, as one token sequence.

    Strings are enumerated in NUMERIC order -- by length, then
    lexicographically, which is Chapter 2's order -- and filtered through
    the DFA, so the corpus holds every accepted string up to a length with
    nothing skipped and nothing repeated.
    """
    from jove.Def_DFA import accepts_dfa
    from jove.LangDef import nthnumeric
    acc = [s for s in (nthnumeric(i, list(alphabet)) for i in range(upto))
           if accepts_dfa(D, s)]
    seq = []
    for s in acc:
        seq += [int(c) for c in s] + [END]
    return acc, seq


def train(seq, k=3, iters=400, seed=1337, n_embd=32, lr=3e-3,
          report_every=0, quiet=True):
    """Train the baby GPT to predict the next token from the last k.

    `iters=0` returns the model UNTRAINED, which is worth looking at: the
    chain it induces is already a complete finite-state machine, with every
    arrow near 1/v because the weights are still random.  Training moves
    the arrows; it does not create the states.

    `report_every=n` prints the loss every n iterations, so the descent is
    visible rather than asserted.
    """
    import contextlib
    import io
    t = _load()
    torch, F = t['torch'], t['F']
    cfg = t['GPTConfig'](block_size=k, vocab_size=3, n_layer=4, n_head=4,
                         n_embd=n_embd, bias=False)
    X = torch.tensor([seq[i:i + k] for i in range(len(seq) - k)],
                     dtype=torch.long)
    Y = torch.tensor([seq[i + k] for i in range(len(seq) - k)],
                     dtype=torch.long)
    torch.manual_seed(seed)
    with contextlib.redirect_stdout(io.StringIO()):
        g = t['GPT'](cfg)                    # it prints its parameter count
    opt = torch.optim.AdamW(g.parameters(), lr=lr, weight_decay=1e-1)
    loss = F.cross_entropy(g(X), Y)          # the loss before any step
    hist = [(0, loss.item())]
    if report_every:
        print('%6s  %9s' % ('iter', 'loss'))
        print('%6d  %9.4f   <- before training' % (0, hist[0][1]))
    for i in range(1, iters + 1):
        loss = F.cross_entropy(g(X), Y)
        loss.backward()
        opt.step()
        opt.zero_grad()
        hist.append((i, loss.item()))
        if report_every and (i % report_every == 0 or i == iters):
            print('%6d  %9.4f' % (i, loss.item()))
    g.history = hist
    g.final_loss = loss.item()
    g.examples = len(X)
    g.k = k
    if not quiet:
        print('%d examples, final loss %.4f' % (len(X), g.final_loss))
    return g


def plot_loss(g, ax=None):
    """The training curve, with log 2 marked.  Returns the figure.

    log 2 = 0.693 is what a fair coin over two symbols costs.  It is not a
    floor here -- the corpus carries a third token, END -- but it is the
    number to have in mind: a model that has learned nothing about the
    language pays about that, and the interesting part of the curve is
    everything below where it starts.
    """
    import math as _m
    import matplotlib.pyplot as plt
    if not getattr(g, 'history', None):
        raise ValueError('no history: train() records it, iters must be > 0')
    xs = [i for i, _ in g.history]
    ys = [v for _, v in g.history]
    if ax is None:
        _, ax = plt.subplots(figsize=(6.2, 3.4))
    ax.plot(xs, ys, color='#1a53c0', lw=1.8)
    ax.axhline(_m.log(2.0), color='#b3251f', ls='--', lw=1,
               label='log 2 = %.3f' % _m.log(2.0))
    ax.scatter([xs[0]], [ys[0]], color='#1a53c0', zorder=3)
    ax.annotate('before training\n%.3f' % ys[0], (xs[0], ys[0]),
                textcoords='offset points', xytext=(12, 2), fontsize=8,
                color='#333')
    ax.annotate('%.3f' % ys[-1], (xs[-1], ys[-1]), textcoords='offset points',
                xytext=(-34, 8), fontsize=8, color='#333')
    ax.set_xlabel('training iteration')
    ax.set_ylabel('cross-entropy loss')
    ax.set_title('what the model learned, and how fast', fontsize=10)
    ax.legend(fontsize=8, frameon=False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return ax.figure


def dist(g, window):
    """The next-token distribution after `window`: [P(0), P(1), P(END)]."""
    t = _load()
    x = t['torch'].tensor(list(window), dtype=t['torch'].long)[None, ...]
    return t['nn'].functional.softmax(g(x), dim=-1)[0].tolist()


def windows_seen(seq, k):
    """The k-windows of actual symbols that occur in the corpus.

    A window the training data never contains is one the model was
    never shown, and asking it about one measures nothing.  For
    'no two 1s in a row' the window 11 is exactly that: it cannot
    occur inside an accepted string, so the model's opinion of it is
    whatever initialisation left behind.
    """
    out = set()
    for i in range(len(seq) - k + 1):
        w = seq[i:i + k]
        if END not in w:
            out.add(''.join(map(str, w)))
    return out


def report(g, D, k=3, show=True, seen=None):
    """Can acceptance be READ OFF P(END)?  (separated, margin, rows)

    Not "is P(END) above some threshold": that question has no fixed
    answer, because P(END) also carries how LIKELY a string is to stop
    here, not merely whether it may.  On a language where almost every
    window is accepted the model quite correctly puts a small probability
    on ending everywhere, and a threshold test then scores it zero -- which
    is what a first version of this function did, and it disagreed with the
    theory for exactly that reason.

    The honest question is SEPARATION: is every accepted window ranked
    above every rejected one?  That is threshold-free, it is what "the
    model has learned the acceptance condition" actually means, and the
    margin between the two groups says how cleanly.
    """
    from jove.Def_DFA import accepts_dfa
    rows = []
    for w in itertools.product((0, 1), repeat=k):
        s_ = ''.join(map(str, w))
        if seen is not None and s_ not in seen:
            continue          # never in the corpus: the model has no opinion
        rows.append((s_, dist(g, w), accepts_dfa(D, s_)))
    yes = [p[2] for _, p, ok in rows if ok]
    no = [p[2] for _, p, ok in rows if not ok]
    if not yes or not no:
        if show:
            print('of the %d window(s) the corpus actually contains, every one '
                  'is %s' % (len(rows), 'accepted' if yes else 'rejected'))
            print('so at k = %d there is nothing for P(END) to separate -- this'
                  % k)
            print('language constrains what may FOLLOW, not where you may stop.')
        return None, None, rows
    sep = min(yes) > max(no)
    margin = min(yes) - max(no)
    if show:
        w0 = max(k, 6)
        print('%-*s  %6s %6s %7s   %s'
              % (w0, 'window', 'P(0)', 'P(1)', 'P(END)', 'accepted?'))
        for s_, p, ok in sorted(rows, key=lambda r: -r[1][2]):
            print('%-*s  %6.2f %6.2f %7.2f   %s'
                  % (w0, s_, p[0], p[1], p[2], 'yes' if ok else 'no'))
        print()
        print('accepted windows  P(END) in [%.2f, %.2f]' % (min(yes), max(yes)))
        print('rejected windows  P(END) in [%.2f, %.2f]' % (min(no), max(no)))
        print()
        if sep:
            print('SEPARATED by a margin of %.2f -- sort the windows by '
                  'P(END) and' % margin)
            print('the accepted ones are exactly the top %d.' % len(yes))
        else:
            print('NOT separated: the two groups overlap, so no threshold on')
            print('P(END) recovers the language.  The model cannot tell these')
            print('windows apart.')
    return sep, margin, rows


def plot_chain(g, k=None, engine='circo', end_node=True, thresh=0.01):
    """The model AS a finite-state machine, drawn the way Karpathy drew it.

    One node per window of k symbols, and an arrow for each token showing
    the probability the model assigns to it -- so an untrained model is a
    complete graph of 50/50 arrows, and a trained one has most of its mass
    on the transitions the language allows.

    The END token gets its own node rather than an arrow back into the
    ring: END is where a string STOPS, and drawing it as a shift would say
    the opposite.  Arrows below `thresh` are dropped so the trained picture
    is readable; that is a drawing decision, and the numbers in report()
    are the ones to quote.
    """
    import graphviz
    k = k or getattr(g, 'k', 3)
    dot = graphviz.Digraph(comment='baby GPT as a Markov chain', engine=engine)
    dot.attr('node', shape='circle', fontname='Helvetica', fontsize='11')
    dot.attr('edge', fontname='Helvetica', fontsize='9')
    if end_node:
        dot.node('END', shape='doublecircle', color='#0f8a4a',
                 fontcolor='#0f8a4a')
    for w in itertools.product((0, 1), repeat=k):
        here = ''.join(map(str, w))
        dot.node(here)
        p = dist(g, w)
        for tok in (0, 1):
            nxt = ''.join(map(str, w[1:] + (tok,)))
            if p[tok] >= thresh:
                dot.edge(here, nxt, label='%d (%.0f%%)' % (tok, 100 * p[tok]),
                         color='#1a53c0' if tok else '#b3251f')
        if end_node and p[2] >= thresh:
            dot.edge(here, 'END', label='END (%.0f%%)' % (100 * p[2]),
                     color='#0f8a4a', style='dashed')
    return dot


# ---- the automata half: no torch, no training --------------------------

def _dhat(D, q, w):
    for c in w:
        q = D['Delta'][(q, c)]
    return q


def _live(M):
    """States of M from which some accepting state is still reachable.

    A corpus of ACCEPTED strings never visits a dead state, so the model is
    never shown one and cannot be blamed for not knowing about it.  The
    window test has to be asked about the part of the machine the data
    actually exercises, or it reports "unlearnable" for languages a
    one-symbol window handles perfectly -- "no two 1s in a row" is exactly
    that case, and getting this wrong made the table disagree with the
    experiment.
    """
    live = set(M['F'])
    changed = True
    while changed:
        changed = False
        for q in M['Q']:
            if q in live:
                continue
            if any(M['Delta'][(q, c)] in live for c in M['Sigma']):
                live.add(q)
                changed = True
    return live


def k_local(D, k):
    """Can ANY context-k model represent this language?  (ok, window, states)

    The model's state is the last k symbols.  If two prefixes that stay
    inside the language share their last k symbols but land in different
    states of the MINIMAL DFA, those states are distinguishable -- some
    suffix separates them -- while the model sees the same input in both
    cases.  It must be wrong on one of them, for any weights and any
    corpus.

    Only LIVE states count, and only windows realisable without dying: the
    training data is accepted strings, so a path that leaves the language
    is one the model is never shown.
    """
    from jove.Def_DFA import min_dfa
    M = min_dfa(D)
    live = _live(M)
    Sig = sorted(M['Sigma'])
    for w in map(''.join, itertools.product(Sig, repeat=k)):
        land = set()
        for q in sorted(live):
            r = q
            for c in w:
                r = M['Delta'][(r, c)]
                if r not in live:
                    r = None
                    break
            if r is not None:
                land.add(r)
        if len(land) > 1:
            return False, w, sorted(land)
    return True, None, None


def colliding_prefixes(D, k, upto=800):
    """Two strings sharing their last k symbols that the DFA must separate.

    The counterexample at its most concrete: feed the model either one and
    it is in the same state, yet the language demands different answers.
    """
    from jove.Def_DFA import min_dfa
    from jove.LangDef import nthnumeric
    M = min_dfa(D)
    seen = {}
    for i in range(upto):
        s = nthnumeric(i, sorted(M['Sigma']))
        if len(s) < k:
            continue
        tail, q = s[-k:], _dhat(M, M['q0'], s)
        if tail in seen and seen[tail][1] != q:
            return seen[tail][0], s, tail
        seen.setdefault(tail, (s, q))
    return None, None, None
