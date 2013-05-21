#!/usr/bin/perl
#
# preload x and y positions for feed motions
#

use strict;
use Getopt::Std;

sub usage
{
  print "usage:\n";
  print " [-f inp]              input gcode file (defaults to stdin)\n";
  print " [-o out]              output gcode file (defaults to stdout)\n";
  print " [-h]                  help (this screen)\n";
}

open(my $fh_inp, "-");
open(my $fh_out, ">-");
my %opts;
getopts("f:o:h", \%opts);

if (exists($opts{h})) { usage(); exit; }
open($fh_inp, $opts{f}) if ($opts{f});
open($fh_out, ">$opts{o}") if ($opts{o});

my @gcode;
while (<$fh_inp>)
{
  push @gcode, $_;
}
close $fh_inp if fileno $fh_inp != fileno STDIN;

my %state;

$state{x} = undef;
$state{prev_x} = undef;
$state{y} = undef;
$state{prev_y} = undef;
$state{z} = undef;
$state{prev_z} = undef;
$state{g} = undef;
$state{line_no} = 0;

$state{del_x} = 1;
$state{del_y} = 1;
$state{del_z} = 1;

$state{z_up}  = 1;

$state{x_dir} = 0;
$state{y_dir} = 0;
$state{z_dir} = 0;

my $op;
my $operand;

foreach my $line (@gcode)
{
  chomp($line);
  $state{line_no}++;

  if ( ($line =~ /^\s*;/) or
       ($line =~ /^\s*$/) )
  {
    print $line, "\n";
    next;
  }

  while ($line)
  {

    # print comment
    if (is_comment($line))
    {
      ($op, $line) = chomp_comment($line);
      print $op;
      next;
    }

    if (is_op($line))
    {
      ($op, $operand, $line) = chomp_op($line);

      state_g($operand) if ( is_op_g($op) ) ;
      state_m($operand) if ( is_op_m($op) ) ;

      state_x($operand) if ( is_op_x($op) ) ;
      state_y($operand) if ( is_op_y($op) ) ;
      state_z($operand) if ( is_op_z($op) ) ;

      print "$op $operand"; 

      next;
    }

    print $line, " ( unprocessed )\n";
    $line = '';

  }
  print "\n";

}

sub is_comment
{
  my $l = shift;
  return $l =~ /^\s*\([^\)]*\)/;
}

sub chomp_comment
{
  my $l = shift;
  $l =~ /^\s*\([^\)]*\)\s*/;
  my $c = substr $l, 0, @+[0];
  $l =~ s/^\s*\([^\)]*\)\s*//;
  return ($c, $l);
}

sub is_op
{
  my $l = shift;
  return $l =~ /^\s*([^\d-]+\s*)+/;
}

sub chomp_op
{
  my $l = shift;
  
  $l =~ /^\s*([^\d-]+\s*)+/;

  my $op = substr $l, 0, @+[0];
  $l =~ s/^\s*([^\d-]+\s*)+//;

  die "parse error at line $state{line_no} ($l, $op)" if (! ($l =~ /^\s*(-?(\d+\s*))+/));
  my $operand = substr $l, 0, @+[0];

  $l =~ s/^\s*(-?(\d+\s*))+//;

  return ($op, $operand, $l);
}

sub is_op_g { my $l = shift; return $l =~ /^\s*[gG]\s*$/; }
sub is_op_m { my $l = shift; return $l =~ /^\s*[mM]\s*$/; }
sub is_op_t { my $l = shift; return $l =~ /^\s*[tT]\s*$/; }
sub is_op_x { my $l = shift; return $l =~ /^\s*[xX]\s*$/; }
sub is_op_y { my $l = shift; return $l =~ /^\s*[yY]\s*$/; }
sub is_op_z { my $l = shift; return $l =~ /^\s*[zZ]\s*$/; }

sub state_g0 { my $l = shift; $state{g} = 0; }
sub state_g1 { my $l = shift; $state{g} = 1; }
sub state_g2 { my $l = shift; $state{g} = 2; }
sub state_g3 { my $l = shift; $state{g} = 3; }

sub state_g
{
  my $g = shift;
  $state{g} = $g;
}

sub state_x 
{
  my $x = shift;

  my $prev_dir = $state{x_dir};

  $state{x_dir} = ( ($x > $state{x}) ? 1 : -1 ) if (defined($state{x}));
  $state{prev_x} = $state{x};
  $state{x} = $x;

  state_x_dir_change() if ($prev_dir != $state{x_dir});
}

sub state_y
{
  my $y = shift;

  my $prev_dir = $state{y_dir};

  $state{y_dir} = ( ($y > $state{y}) ? 1 : -1 ) if (defined($state{y}));
  $state{prev_y} = $state{y};
  $state{y} = $y;

  state_y_dir_change() if ($prev_dir != $state{y_dir});
}

sub state_z
{
  my $z = shift;

  my $prev_dir = $state{z_dir};

  $state{z_dir} = ( ($z > $state{z}) ? 1 : -1 ) if (defined($state{z}));
  $state{prev_z} = $state{z};
  $state{z} = $z;

  state_z_dir_change() if ($prev_dir != $state{z_dir});
}

sub state_x_dir_change 
{
  return if ($state{g} == 0);

  print "\n( x dir change start )\n"; 

  print "g1 z", $state{z_up}, "\n";
  if ($state{x_dir} > 0)
  {
    print "g1 x", $state{prev_x} - $state{del_x}, "\n";
  }
  elsif ($state{x_dir} < 0)
  {
    print "g1 x", $state{prev_x} + $state{del_x}, "\n";
  }
  print "g1 x", $state{prev_x}, "\n";
  print "g1 z", $state{z}, "\n";

  print "( x dir change end )\n"; 

  print "\n";
}

sub state_y_dir_change 
{ 
  return if ($state{g} == 0);

  print "\n( y dir change start )\n"; 

  print "g1 z", $state{z_up}, "\n";
  if ($state{y_dir} > 0)
  {
    print "g1 y", $state{prev_y} - $state{del_y}, "\n";
  }
  elsif ($state{y_dir} < 0)
  {
    print "g1 y", $state{prev_y} + $state{del_y}, "\n";
  }
  print "g1 y", $state{prev_y}, "\n";
  print "g1 z", $state{z}, "\n";

  print "( y dir change end )\n"; 

  print "\n";
}

sub state_z_dir_change 
{ 
  # nop
}

close $fh_out if fileno $fh_out != fileno STDOUT;

