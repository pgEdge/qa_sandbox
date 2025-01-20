# This test case runs the command:
# ./nc service status 
# without pgV.

use strict;
use warnings;

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;

my $homedir = "$ENV{EDGE_HOME_DIR}";
my $cli = $ENV{EDGE_CLI};
my $pgversion = $ENV{EDGE_COMPONENT};

# Checks for service status without providing a component name that should by default bring the status of installed pgV

my $cmd = qq($homedir/$cli service status);
print("cmd = $cmd\n");
my ($stdout_buf)= (run_command_and_exit_iferr ($cmd))[3];
print("stdout_buf = @$stdout_buf\n");

# This test should return a message that contains the word 'port' regardless of the test case it follows:
if (contains($stdout_buf->[0], "port"))
 {
    exit(0);
 }
 else
 {
    exit(1);
 }
