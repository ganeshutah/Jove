# PcpJupyter.py
#
# Python interface with Ling Zhao's PCP solver (https://github.com/chrozz/PCPSolver)

import subprocess
import re
import pdb
import platform
import os

def pcp_oslink():
	"""
	Determines the underlying os to select the symlink the appropriate pcp binary
	"""
	platform_name = platform.platform()
	platform.platform()
	src = 'pcpbinaries/pcp_linux'
	dst = './Jove/jove/pcp'
	if('windows' in platform_name.lower()):
		print("Detected platform windows; PLEASE be running with Admin Privileges!")
		src = 'pcpbinaries\pcp_win.exe'
		dst = 'pcp.exe'
	elif ('linux' in platform_name.lower()):
		print("Detected platform linux")
		src = 'pcpbinaries/pcp_linux'
	elif ('darwin' in platform_name.lower()):
		print("Detected platform Darwin")
		src = 'pcpbinaries/pcp_mac'
	else:
		print("??? Undetected Platform : Compile for your os and")
		print("Edit pcp_oslink() function to add an elif option for your os")
		sys.exit()
	if(os.path.isfile(dst) or os.path.islink(dst)):
                try:
                        os.remove(dst)
                except OSError:
                        print("Tried to remove ", dst, " but that failed.")       
	try:
                os.symlink(src, dst)
        except OSError:
                print("Tried to symlink ", src, " with ", dst, " but that failed.")
	return dst
		
		


def pcp_solve(pcp_pairs, run=None, ni=False, di=None, depth=None, tiles_per_row=15):
    """
    Forward user input to a file, which we then use Ling Zhao's pcp solver to solve.

    :param pcp_pairs: List of tuple pairs representing pcp 'tiles'
    :param run: Number of runs to perform.
    :param ni: No iterative search.
    :param di: Depth increment.
    :param depth: Search depth.
    :param tiles_per_row: Number of tiles to show in single row together (useful for creating more meaningful output)
    """

    # Build pcp instance string for the solver.
    pcp_pair_num = len(pcp_pairs)
    largest_pcp_string = 0

    pcp_top = ""
    pcp_bottom = ""

    for pair in pcp_pairs:
        # Build the strings for the pcp solver.
        pcp_top += str(pair[0]) + " "
        pcp_bottom += str(pair[1]) + " "

        # Determine the largest size of tile (needed for pcp solver).
        if len(str(pair[0])) > largest_pcp_string:
            largest_pcp_string = len(str(pair[0]))
        if len(str(pair[1])) > largest_pcp_string:
            largest_pcp_string = len(str(pair[1]))

    # Build final pcp instance for the solver.
    pcp_instance = str(pcp_pair_num) + " " + str(largest_pcp_string) + "\n" + pcp_top + "\n" + pcp_bottom

    # Write their pcp instance to a file to be used.
    file = open("temp.txt", "w")
    file.write(pcp_instance)
    file.close()

    # Build the method call.
    #args = "./pcpbinaries/pcp_win.exe -i temp.txt"
    args = pcp_oslink()+" -i temp.txt"

    # Add supplied user arguments.
    if run is not None:
        if type(run) is int:
            args += " -r " + str(run)
        else:
            raise Exception("Type of supplied argument run should be an integer.")

    if di is not None:
        if type(di) is int:
            args += " -di " + str(di)
        else:
            raise Exception("Type of supplied argument di (depth increment) should be an integer.")

    if depth is not None:
        if type(depth) is int:
            args += " -d " + str(depth)
        else:
            raise Exception("Type of supplied argument depth should be an integer.")

    if ni:
        args += " -ni"

    # Run the command.
    print(" Running the command ... : ", args.split())
    process = subprocess.Popen(args.split(), stdout=subprocess.PIPE)
    ouput, error = process.communicate()

    # Grab the solution info from the generated file.
    solved = open("sol.txt", "r").read()

    backwards = solved.__contains__("Choose the reverse direction:")

    # Split to get the solution(s)
    split_string = re.split("Find the solution in depth: [0-9]+ \([a-zA-Z0-9: ]+\)", solved)

    if len(split_string) > 1:
        # If we are here, the above RegEx is matched, meaning we have found a solution.
        print("Solution(s) to PCP instance:\n")
        for x in range(1, len(split_string)):
            print("Solution " + str(x))
            sol = split_string[x]
            final_ans = []

            # Grab out the actual solution.
            for ans in re.findall("\\n[ 0-9]+", sol):
                ans = ans.replace("\n", "").split("  ")

                # Convert to integers and remove empty spaces.
                for ans_part in ans:
                    if not(ans_part == ""):
                        final_ans.append(int(ans_part))

            # Print out the list of tiles.
            print(final_ans)

            final = ""

            ans_top = ""
            ans_bottom = ""

            counter = 0

            # Print out as the actual tile values:
            for tile_num in final_ans:
                tile = pcp_pairs[tile_num-1]
                ans_top += _buffer_word(str(tile[0]), largest_pcp_string, backwards)
                ans_bottom += _buffer_word(str(tile[1]), largest_pcp_string, backwards)
                counter += 1
                if counter == tiles_per_row:
                    final += ans_top + "\n" + ans_bottom + "\n\n"
                    counter = 0
                    ans_top = ""
                    ans_bottom = ""

            final += ans_top + "\n" + ans_bottom + "\n\n"

            print(final)
    else:
        # No solution exists.
        print("No solution exists for the provided PCP instance.")


def _buffer_word(word, length, backward):
    """
    Simple helper that adds spaces to the end of the provided word so that it will look uniform.
    :param word: word (as a string) to buffer
    :param length: 1 less than the length to buffer to
    :param backward: Whether the provided string should be made backwards (used by the solver for convenience)
    :return: buffered word
    """
    if backward:
        word = word[::-1]

    while len(word) < length + 1:
        word += " "

    return word
