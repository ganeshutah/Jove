<html>
<head>
<title>PBL Interface</title>
<link rel="stylesheet" type="text/css" href="styles/index.css">
<link rel="stylesheet" type="text/css"
	href="styles/bootstrap-responsive.css">

<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"
	type="text/javascript"></script>
<script src="scripts/pbl.js"></script>
<script src="scripts/bootstrap.js"></script>

<META NAME="Description" CONTENT="An online Python propositional logic webapp. Converts formula into equivalent cnf or nne forms.">

<META NAME="KeyWords" CONTENT="BDD, Python, Binary Decision Diagram, boolean, logic, propositional, sat, cnf, nne, Tyler Sorensen, Ganesh Gopalakrishnan">

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
						<li class="active"><a href="PBL.php">PBL Interface</a></li>
						<li><a href="BDD.php">BDD Interface</a></li>
						<li><a href="Download.php">Download</a>
						<li><a href="people.php">People</a></li>
						<li><a href="http://www.cs.utah.edu/formal_verification/">Gauss Group</a></li>
						<li><a href="http://www.utah.edu">The University Of Utah</a></li>
					</ul>
				</div>
			</div>
		</div>
	</div>

	<!-- body -->
	<div class="container">
		<div class="hero-unit">
			<h2>This is the online interface for PBL, a Boolean algebra/propositional logic library written in Python.</h2>
			
				<!-- about the PBL package -->
				<a href="#myModal" role="button" class="btn btn-primary" data-toggle="modal"><h3>About the PBL package</h3></a>
				
				<!-- Modal -->
				<div id="myModal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
 					 <div class="modal-header">
    					<button type="button" class="close" data-dismiss="modal" aria-hidden="true">¡Á</button>
   						<h2 id="myModalLabel">About the PBL package</h2>
	  				</div>
	  				
	 				<div class="modal-body">
		 				<p>
						You may either scroll through the examples or enter your own boolean or propositional formulas in the ENTER YOUR FORMULA box.
						Although PBL has many other features, the online interface allows you convert the formula to cnf (exponentially sized)
						or negation normal form. The syntax was made to be robust and intuitive. See the examples to get an idea. The exact language
						spec can be seen here. These are only two features of PBL. Other features include:</p>
	 				<ul>	
						<li>Parsing files <a href="http://logic.pdmi.ras.ru/~basolver/dimacs.html">dimacs files</a></li>
						<li>Parsing files custom language (like in examples)</li>
						<li>Convert to <a href="http://en.wikipedia.org/wiki/Conjunctive_normal_form">cnf</a>, 
							<a href="http://en.wikipedia.org/wiki/Negation_normal_form">nne</a>, or polynomial sized cnf</li>
						<li>Output dimacs file</li>
						<li>Propagate variable values </li>
	 				</ul>
	 				
	 				<p>
	 				Parsing is accomplished using the <a href="http://www.dabeaz.com/ply/">PLY</a> library 
					<br>
					<br>
					This library makes a good base to write various SAT algorithms including DPLL and BDDs.
					<br>
					<br>
					This package implements algorithms from the Bradley and Manna book "The Calculus of Computation"
					<br>
					<br>
					Currently there is no simplification algorithms implemented. Email me if you are interested in contributing :)
					<br>
					<br>
					These tools are mostly for educational purposes! There are probably better choices for large, robust projects.
	 				</p>
	    				

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
					
					<b>Sub-Formulas :</b> Pretty much a place holder for boolean expressions, allows you to 
					create large formulas easily. Is not considered in the actual BDD unless specified
					in the Main_Exp.<br>
					<i>variable = Expression</i><br>
					variable now refers to expression and can be used later on.<br><br>
					
					<b>Expressions : </b>A boolean expression, defined recursively as:
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
				<textarea class="PBLFormulaArea">
				</textarea>
				</div>
				
				<div class="span5">
				<h3>PROGRAM OUTPUT</h3>
				<textarea class="PBLOutputArea">
				</textarea>
				</div>			
			</div>

			<div>
				<button class="btn btn-inverse" id="PBLPrevious">Prev</button>
				<button class="btn btn-inverse" id="PBLNext">Next</button>
				<button class="btn btn-info" id="convertToNNE">Convert To NNE</button>
				<button class="btn btn-success" id="convertToCNF">Convert To CNF</button>
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
