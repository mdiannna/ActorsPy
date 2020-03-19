
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RED = '\033[31m' 
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_warning(text):
	print(bcolors.WARNING + str(text) + bcolors.ENDC)

def print_error(text):
	print(bcolors.RED + str(text) + bcolors.ENDC)

def print_blue(text):
	print(bcolors.OKBLUE + str(text) + bcolors.ENDC)

def print_green(text):
	print(bcolors.OKGREEN + str(text) + bcolors.ENDC)
	
def green(text):
	return bcolors.OKGREEN + str(text) + bcolors.ENDC

def print_success(text):
	print(bcolors.OKGREEN + str(text) + bcolors.ENDC)

def bold(text):
	return bcolors.BOLD + str(text) + bcolors.ENDC

def underline(text):
	return bcolors.UNDERLINE + str(text) + bcolors.ENDC

def print_header(text):
	print(bcolors.HEADER + "-------------------" + bcolors.ENDC)
	print(bcolors.HEADER + str(text) + bcolors.ENDC)
	print(bcolors.HEADER + "-------------------" + bcolors.ENDC)
