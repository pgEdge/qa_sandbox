# This test case runs the command:
# ./nc service stop pgV
# and performs the necessary validation before and after.

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
my $exitcode = 0;
#
# We use nodectl to service stop pg16.
# 

# Checking service status
my $cmd0 = qq($homedir/$cli service status $pgversion);
print("cmd = $cmd0\n");
my ($stdout_buf0)= (run_command_and_exit_iferr ($cmd0))[3];
print("stdout_buf0 : @$stdout_buf0");

# If server is running, we attempt to service stop it
if (contains($stdout_buf0->[0], "running on port"))
 {
    my $cmd = qq($homedir/$cli service stop $pgversion);
    print("cmd = $cmd\n");
    my ($stdout_buf)= (run_command_and_exit_iferr ($cmd))[3];
    print("stdout_buf : @$stdout_buf");
    # if service stop was successfuly able to stop the server
    if(contains($stdout_buf->[0], "stopping"))
    {
        print("$pgversion stopped successfully. Exiting with success");
        $exitcode = 0;
    }
    else
    {
        print("$pgversion already stopped. Start the server so we can start it.\n");
        # service start pgV
        my $cmd1 = qq($homedir/$cli service start $pgversion);
        print("cmd1 = $cmd1\n");
        my ($stdout_buf1)= (run_command_and_exit_iferr ($cmd1))[3];
        print("stdout_buf1 : @$stdout_buf1");

        # if service start was successful 
        if(contains($stdout_buf1->[0], "started"))
        {
          print("$pgversion started - next we stop it.\n");
          # service stop pgV
          my $cmd2 = qq($homedir/$cli service stop $pgversion);
          print("cmd2 = $cmd2\n");
          my ($stdout_buf2)= (run_command_and_exit_iferr ($cmd2))[3];
          print("stdout_buf2 : @$stdout_buf2");
        }

        else
        {
          $exitcode = 1;
        }

    }
}


