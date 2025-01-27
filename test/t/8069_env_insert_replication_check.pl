# This is part of a complex test case; after creating a two node cluster on the localhost, 
# the test case executes the commands in the Getting Started Guide at the pgEdge website.
#
# In this case, we'll register node 1 and create the repset on that node.
# Checks Table existence
# Checks Repset through spock.replication_set
# Checks tables through nc spock repset-list-tables
# Validation of adding Table to repset
# Check for the existence of replication set

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;
use DBI;
use List::MoreUtils qw(pairwise);
no warnings 'uninitialized';


# Our parameters are:

print("whoami = $ENV{EDGE_REPUSER}\n");
my $homedir1="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
my $homedir2="$ENV{EDGE_CLUSTER_DIR}/n2/pgedge";
my $myport2 = $ENV{'EDGE_START_PORT'} + 1;
my $seconds = $ENV{'EDGE_SLEEP'};


print("The home directory is $homedir1\n"); 

print("The home directory is $homedir2\n"); 


# We can retrieve the port number from nodectl in json form...

print("The port number is {$ENV{EDGE_START_PORT}}\n");

print("The port number is {$myport2}\n");




#====================================================================================================================================================
# Checking Replication --delete=False
   
    print("INSERT=FALSE REPLICATION CHECK\n");
    
    print ("-"x45,"\n");
    my $cmd6= qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "INSERT INTO public.foo values(888)");
    print("cmd6 = $cmd6\n");
    my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
    
    print("stdout_buf6= @$stdout_buf6\n");
    
    if(!(contains(@$stdout_buf6[0], "INSERT")))
{
    exit(1);
}
       print ("-"x100,"\n"); 
    

    print("INSERT=FALSE REPLICATION CHECK IN NODE n1 \n");
    
     print ("-"x45,"\n");
      # Listing table contents of Port1 6432
      
     my $cmd9 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM foo");
   print("cmd9 = $cmd9\n");
   my($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);
   print("stdout_buf9= @$stdout_buf9\n");
  print("="x100,"\n");

if(!(contains(@$stdout_buf9[0], "888")))
{
    exit(1);
}
   
  print("="x100,"\n");
  
 # Listing table contents of Port2 6433
 
   print("DELETE=FALSE REPLICATION CHECK IN NODE n2\n");
   
    print ("-"x45,"\n");
  my $cmd10 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "SELECT * FROM foo WHERE col1=888");
   print("cmd10 = $cmd10\n");
   my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);
   print("stdout_buf10= @$stdout_buf10\n");
  print("="x100,"\n");

if(!(contains(@$stdout_buf10[0], "0 row")))
{
    exit(1);
}
 
 
 #====================================================================================================================================================
  
  #Checking Replication insert=True
    print("DELETE FUNCTION REPLICATION CHECK\n");
     print ("-"x45,"\n");
    my $cmd7 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "DELETE FROM foo where col1=2");
    print("cmd7 = $cmd7\n");
    my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);
   
   print ("-"x100,"\n"); 
    
if(!(contains(@$stdout_buf7[0], "DELETE")))
{
    exit(1);
}

      # Listing table contents of Port1 6432
      
     print("INSERT FUNCTION REPLICATION CHECK IN NODE n1 \n");
      print ("-"x45,"\n"); 
    my $cmd8 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM foo where col1=2");
   print("cmd8 = $cmd8\n");
   my($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);
   print("stdout_buf8= @$stdout_buf8\n");
  print("="x100,"\n");

if(!(contains(@$stdout_buf8[0], "0 rows")))
{
    exit(1);
}

  # Listing table contents of Port2 6433
  
    print("INSERT FUNCTION REPLICATION CHECK IN NODE n2 \n");
    print ("-"x45,"\n");
  my $cmd11 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "SELECT * FROM foo where col1=2");
   print("cmd11 = $cmd11\n");
   my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);
   print("stdout_buf11= @$stdout_buf11\n");
  print("="x100,"\n");

if(!(contains(@$stdout_buf11[0], "0 rows")))
{
    exit(1);
}

  #======================================================================================================================================================================
  
   #Checking Replication update=True
   
    print("UPDATE FUNCTION REPLICATION CHECK\n");
     print ("-"x45,"\n");
    my $cmd12 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "UPDATE foo SET col1=333 where col1=3");
    print("cmd12 = $cmd12\n");
    my($success12, $error_message12, $full_buf12, $stdout_buf12, $stderr_buf12)= IPC::Cmd::run(command => $cmd12, verbose => 0);
   
   print ("-"x100,"\n"); 
   
if(!(contains(@$stdout_buf12[0], "UPDATE")))
{
exit(1);
}

      # Listing table contents of Port1 6432
      
     print("UPDATE FUNCTION REPLICATION CHECK IN NODE n1 \n");
      print ("-"x45,"\n"); 
    my $cmd13 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM foo");
   print("cmd8 = $cmd8\n");
   my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);
   print("stdout_buf13= @$stdout_buf13\n");
  print("="x100,"\n");
  
if(!(contains(@$stdout_buf13[0], "333")))
{
    exit(1);
}

  # Listing table contents of Port2 6433
   print("UPDATE FUNCTION REPLICATION CHECK IN NODE n2\n");
    print ("-"x45,"\n");
  my $cmd14 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "SELECT * FROM foo");
   print("cmd14 = $cmd14\n");
   my($success14, $error_message14, $full_buf14, $stdout_buf14, $stderr_buf14)= IPC::Cmd::run(command => $cmd14, verbose => 0);
   print("stdout_buf14= @$stdout_buf14\n");
  print("="x100,"\n");
  
if(!(contains(@$stdout_buf14[0], "333")))
{
    exit(1);
}

  #========================================================================================================================================================================
  
    #Checking Replication Truncate=True
    print("TRUNCATE FUNCTION REPLICATION CHECK\n");
     print ("-"x45,"\n");
    my $cmd15 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "TRUNCATE foo");
    print("cmd15 = $cmd15\n");
    my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);
   
   print ("-"x100,"\n"); 
    
if(!(contains(@$stdout_buf15[0], "TRUNCATE")))
{
    exit(1);
}

      # Listing table contents of Port1 6432
      
     print("TRUNCATE FUNCTION REPLICATION CHECK IN NODE n1\n"); 
      print ("-"x45,"\n"); 
    my $cmd16 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM foo");
   print("cmd16 = $cmd16\n");
   my($success16, $error_message16, $full_buf16, $stdout_buf16, $stderr_buf16)= IPC::Cmd::run(command => $cmd16, verbose => 0);
   print("stdout_buf16= @$stdout_buf16\n");
  print("="x100,"\n");
  
if(!(contains(@$stdout_buf16[0], "0 rows")))
{
    exit(1);
}

  # Listing table contents of Port2 6433
  #
  # print("Adding call to sleep function")
  my $cmd999 = qq(sleep $seconds);
  my($success999, $error_message999, $full_buf999, $stdout_buf999, $stderr_buf999)= IPC::Cmd::run(command => $cmd999, verbose => 0);
  
   print("TRUNCATE FUNCTION REPLICATION CHECK IN NODE n2\n");
    print ("-"x45,"\n");
  my $cmd17 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "SELECT * FROM foo");
   print("cmd17 = $cmd17\n");
   my($success17, $error_message17, $full_buf17, $stdout_buf17, $stderr_buf17)= IPC::Cmd::run(command => $cmd17, verbose => 0);
   print("stdout_buf17= @$stdout_buf17\n");
  print("="x100,"\n");
  
if(!(contains(@$stdout_buf17[0], "0 rows")))
{
    exit(1);
}

  #================================================================================================================================================================================
  
  #Generating series in table of port 1 6432

 print("GENERATING SERIES IN TABLE IN n1\n");
 
   my $cmd18 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "INSERT INTO foo select generate_series(1,10)");
   print("cmd18 = $cmd18\n");
   my($success18, $error_message18, $full_buf18, $stdout_buf18, $stderr_buf18)= IPC::Cmd::run(command => $cmd18, verbose => 0);
 
if(!(contains(@$stdout_buf18[0], "INSERT")))
{
    exit(1);
}

   print("="x100,"\n");
   
   my $cmd20 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM foo");
   print("cmd20 = $cmd20\n");
   my($success20, $error_message20, $full_buf20, $stdout_buf20, $stderr_buf20)= IPC::Cmd::run(command => $cmd20, verbose => 0);
   print("stdout_buf20= @$stdout_buf20\n");
  print("="x100,"\n");
 
if(!(contains(@$stdout_buf20[0], "10 rows")))
{
    exit(1);
}
  
   #================================================================================================================================================================================
   
   #Generating series in table of port 2 6433

   print("GENERATING SERIES IN TABLE IN n2\n");
   
   my $cmd19 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "INSERT INTO foo select generate_series(1,10)");
   print("cmd19 = $cmd19\n");
   my($success19, $error_message19, $full_buf19, $stdout_buf19, $stderr_buf19)= IPC::Cmd::run(command => $cmd19, verbose => 0);
   #print("stdout_buf19= @$stdout_buf19\n");
   print("full_buf19= @$full_buf19\n");
   #print("stderr_buf19= @$stderr_buf19\n");
  
  if((contains(@$full_buf19[0], "INSERT")))
{
    exit(0);
}
   print("="x100,"\n");
   
 my $cmd22 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql  -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "SELECT * FROM foo");
   print("cmd22 = $cmd22\n");
   my($success22, $error_message22, $full_buf22, $stdout_buf22, $stderr_buf22)= IPC::Cmd::run(command => $cmd22, verbose => 0);
   print("stdout_buf22= @$stdout_buf22\n");
  print("="x100,"\n");

if(!(contains(@$stdout_buf22[0], "10 rows")))
{
    exit(1);
}

  
   


    

   #==================================================================================================================================================================================


 
    
    
