<html>
<head>
<title>BDD Interface</title>
<link rel="stylesheet" type="text/css" href="styles/index.css">
<link rel="stylesheet" type="text/css"
	href="styles/bootstrap-responsive.css">
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"
	type="text/javascript"></script>
<script src="scripts/bdd.js"></script>
<script src="scripts/bootstrap.js"></script>
<META NAME="Description" CONTENT="An online Python BDD (Binary Decision Diagram) webapp. Calculates satisfying assignments for Boolean algebra formulas and displays the graph.">

<META NAME="KeyWords" CONTENT="BDD, Python, Binary Decision Diagram, Boolean, logic, propositional, sat, cnf, nne, Tyler Sorensen, Ganesh Gopalakrishnan">

</head>

<body>
	<!-- Header -->
	<div class="navbar navbar-inverse navbar-fixed-top">
		<div class="navbar-inner">
			<div class="container">

				<a class="brand" href="index.php">PBL</a>
				<div class="nav-collapse collapse">
					<ul class="nav">
						<li><a href="index.php">About</a></li>
						<li><a href="PBL.php">PBL Interface</a></li>
						<li class="active"><a href="BDD.php">BDD Interface</a></li>
						<li><a href="Download.php">Download</a></li>
						<li><a href="people.php">People</a></li>
						<li><a href="http://www.cs.utah.edu/formal_verification/">Gauss Group</a></li>
						<li><a href="http://www.utah.edu">The University of Utah</a></li>				
					</ul>
				</div>
			</div>
		</div>
	</div>

	<!-- body -->
	<div class="container">
		<div class="hero-unit">
			<h3>This is the online interface for a BDD package written using PBL.</h3>
			
				<!-- Button to trigger modal -->
				<a href="#myModal" role="button" class="btn btn-primary" data-toggle="modal"><h3>About this BDD implementation</h3></a>
				
				<!-- Modal -->
				<div id="myModal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
 					 <div class="modal-header">
    					<button type="button" class="close" data-dismiss="modal" aria-hidden="true">¡Á</button>
   						<h2 id="myModalLabel">About this BDD implementation</h2>
	  				</div>
	  				
	 				<div class="modal-body">
	 				<ul>
	 					<li>
	 					<p>If you don't know what a BDD is check out the great wikipedia
							<a href="http://en.wikipedia.org/wiki/Binary_decision_diagram">page</a>.
							 Donald Knuth calls BDDs "<em>one of the only really fundamental
							data structures that came out in the last twenty-five years</em>". You
							can watch an excellent lecture by him about BDDs 
							<a href="http://myvideos.stanford.edu/player/slplayer.aspx?coll=ea60314a-53b3-4be2-8552-dcf190ca0c0b&co=18bcd3a8-965a-4a63-a516-a1ad74af1119&o=true">
							here</a>.</p>
	 					</li>
	 					<li><p>You may either scroll through the examples or enter your own
								Boolean formulas in the ENTER YOUR FORMULA box. Select build BDD
								(or build minimum BDD) to build the BDD. A .png graph is generated
								and displayed below and stats about the BDD and formula are
								displayed in the OUTPUT box. The language was created to be robust
								and intuitive, but for info see the examples or the language spec.</p>
						</li>
						<li><p>You may either specify a variable ordering using the "Var_Order"
							keyword or the variables will be ordered in an unspecified way. The
							main expression must be specified using the "Main_Exp" keyword.</p>
						</li>
						
	 					<li><p>The implementation of the BDD is based off of Anderson's notes 
	 					<a href="http://www.configit.com/fileadmin/Configit/Documents/bdd-eap.pdf">
	 					here</a>.</p></li>

						<li><p>The implementation recently incorporated an optimized ite build
							described in the paper: <em>Efficient Implementation of a BDD Package</em></p></li>

						<li><p>The minimum BDD implementation is described in paper:
						<em>Dynamic Variable Ordering for Ordered Binary Decision Diagrams</em>
						</p></li>
	 					
	 				</ul>
	    				
	  				</div>
	  				
	  				<div class="modal-footer">
	    				<button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
	  				</div>
				</div>
				
				<!--Language Spec -->
				<a href="#myModal1" role="button" class="btn btn-warning" data-toggle="modal"><h3>Language Spec</h3></a>
				
				<!-- Modal -->
				<div id="myModal1" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
 					 <div class="modal-header">
    					<button type="button" class="close" data-dismiss="modal" aria-hidden="true">¡Á</button>
   						<h2 id="myModalLabel">Language Spec</h2>
	  				</div>
	  				
	 				<div class="modal-body">
		 			<p>
					PyBool can handle parse DIMACS files, but also a more expressive in-house language.
					A short summary of the language is as follows:<br><br>
					
					<b>Variables :</b> Can be named anything alpha numeric, except for keywords. Literal variables must
					be declared in a Var_Order statement.<br><br>
					
					<b>Var_Order :</b> declares variables and order of variables (important for BDDs) used as such:<br>
					<i>Var_Order : {variable name}</i><br>
					You can have multi Var_Order statements, just don't declare variables multiple times.<br>
					Variables storing sub-formulas should not be in Var_Order statements<br><br>
					
					<b>Constants :</b> Represents logical True or False in expressions<br>
					<i>1 - True<br>
					0 - False</i><br><br>
					
					<b>Sub-Formulas :</b> Pretty much a place holder for Boolean expressions, allows you to 
					create large formulas easily. Is not considered in the actual BDD unless specified
					in the Main_Exp.<br>
					<i>variable = Expression</i><br>
					variable now refers to expression and can be used later on.<br><br>
					
					<b>Expressions : </b>A Boolean expression, defined recursively as:
					<i>Expression {operator Expression}</i><br>
					Where the base cases are Variables or constants as expressions<br><br>
					<b>Operators :</b> Boolean operators applied to expressions (all binary except negation):
					<ul>
					<li> () : parentheses
					<li> ! | ~ : negation
					<li> & : conjunction (and)
					<li> | : disjunction (or)
					<li> => | -> : implication 
					<li> XOR : exclusive-or
					<li> <=> | <-> : iff
					</ul>
					<p>
					They are listed in order of precedence, and => associates from right to left.<br><br>
					
					
					<b>Main_Exp :</b> The only expression considered by the BDD. simply<br>
					<i> Main_Expr : Expression</i><br>
					<br>
					<b>Comments :</b> denoted with #<br><br>
					Please view the examples on the main BDD page for better understanding.
					</p>
	    				

	  				</div>
	  				
	  				<div class="modal-footer">
	    				<button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
	  				</div>
				</div>

			<div class="row">
				<div class="span5">
					<h3>ENTER YOUR FORMULA HERE</h3>
					<textarea class="formulaArea">
				</textarea>
				</div>

				<div class="span5">
					<h3>PROGRAM OUTPUT</h3>
					<textarea class="outputArea">
				</textarea>
				</div>
			</div>

			<div>
				<button class="btn btn-inverse" id="previous">Prev</button>
				<button class="btn btn-inverse" id="next">Next</button>
				<button class="btn btn-info" id="buildBDD">Build BDD</button>
				<button class="btn btn-success" id="buildMinimumBDD">Build minimum
					BDD</button>
			</div>

			<div class="imageArea">
				<h2>GRAPH OUTPUT</h2>
				<img class="imageArea" src="" width="500" />
			</div>
		</div>
		<footer>		
			<p><strong>Please email questions, comments or bugs to Tyler Sorensen<br>
			ALSO IF YOU FIND THIS SITE USEFUL PLEASE LET US KNOW! YOUR FEEDBACK HELPS US TO IMPROVE AND MAINTAIN THIS SITE<br>
			t.sorensen@utah.edu</strong></p>		
		</footer>
	</div>

</body>
</html>
