#!/usr/bin/perl
#
# preload x and y positions for feed motions
#

use strict;
use Getopt::Std;

$Getopt::Std::STANDARD_HELP_VERSION = 1;

my $VERSION_STR = "0.1 alpha";

sub VERSION_MESSAGE {
  print "ngc_scale version ", $VERSION_STR, "\n"
}

sub usage
{
  print "usage:\n";
  print " [-f inp]              input gcode file (defaults to stdin)\n";
  print " [-o out]              output gcode file (defaults to stdout)\n";
  print " [-s s]                x,y,z scaling factor (overrides -X, -Y, -Z)\n";
  print " [-x x_scale]          scale in the x direction\n";
  print " [-y y_scale]          scale in the y direction\n";
  print " [-z z_scale]          scale in the z direction\n";
  print " [-h|--help]           help (this screen)\n";
  print " [--version]           print version number\n";
}

sub HELP_MESSAGE {
  usage();
}

usage() and exit(0) if (scalar(@ARGV) == 0);

open(my $FH_INP, "-");
open(my $FH_OUT, ">-");
my %opts;
getopts("f:o:x:y:z:s:h", \%opts);

my $s_scale = 1.0;

my $x_scale = 1.0;
my $y_scale = 1.0;
my $z_scale = 1.0;

if (exists($opts{h})) { usage(); exit; }
open($FH_INP, $opts{f}) if ($opts{f});
open($FH_OUT, ">$opts{o}") if ($opts{o});

$x_scale = $opts{x} if ($opts{x});
$y_scale = $opts{y} if ($opts{y});
$z_scale = $opts{z} if ($opts{z});

# s_scale overrides x and y scale
if ($opts{s})
{
  $s_scale = $opts{s};
  $x_scale = $s_scale;
  $y_scale = $s_scale;
  $z_scale = $s_scale;
}


my @gcode;
while (<$FH_INP>)
{
  push @gcode, $_;
}
close $FH_INP if fileno $FH_INP != fileno STDIN;

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

print $FH_OUT "( x_scale $x_scale, y_scale $y_scale )\n";

foreach my $line (@gcode)
{
  chomp($line);
  $state{line_no}++;

  if ( ($line =~ /^\s*;/) or
       ($line =~ /^\s*$/) )
  {
    print $FH_OUT $line, "\n";
    next;
  }


  while ($line)
  {

    if ($line =~ /^\s*$/)
    {
      $line = "";
      next;
    }

    # print comment
    if (is_comment($line))
    {
      ($op, $line) = chomp_comment($line);
      print $FH_OUT $op;
      next;
    }


    if (is_op($line))
    {

      ($op, $operand, $line) = chomp_op($line);

      state_f($operand) if ( is_op_f($op) ) ;
      state_s($operand) if ( is_op_s($op) ) ;

      state_g($operand) if ( is_op_g($op) ) ;
      state_m($operand) if ( is_op_m($op) ) ;

      state_x($operand) if ( is_op_x($op) ) ;
      state_y($operand) if ( is_op_y($op) ) ;
      state_z($operand) if ( is_op_z($op) ) ;

      state_i($operand) if ( is_op_i($op) ) ;
      state_j($operand) if ( is_op_j($op) ) ;

      state_p($operand) if ( is_op_p($op) ) ;

      next;
    }

    print $FH_OUT $line, " ( unprocessed )\n";
    $line = '';

  }
  print $FH_OUT "\n";

}
close $FH_OUT if fileno $FH_OUT != fileno STDOUT;

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

  die "parse error at line $state{line_no} ($l, $op)" if (! ($l =~ /^\s*(-?\d+\s*(\.\s*\d+)?)/));
  my $operand = substr $l, 0, @+[0];

  $l =~ s/^\s*(-?\s*\d+\s*(\.\s*\d+)?)//;

  return ($op, $operand, $l);
}

sub is_op_f { my $l = shift; return $l =~ /^\s*[fF]\s*$/; }
sub is_op_s { my $l = shift; return $l =~ /^\s*[sS]\s*$/; }

sub is_op_g { my $l = shift; return $l =~ /^\s*[gG]\s*$/; }
sub is_op_m { my $l = shift; return $l =~ /^\s*[mM]\s*$/; }
sub is_op_t { my $l = shift; return $l =~ /^\s*[tT]\s*$/; }
sub is_op_x { my $l = shift; return $l =~ /^\s*[xX]\s*$/; }
sub is_op_y { my $l = shift; return $l =~ /^\s*[yY]\s*$/; }
sub is_op_z { my $l = shift; return $l =~ /^\s*[zZ]\s*$/; }

sub is_op_i { my $l = shift; return $l =~ /^\s*[iI]\s*$/; }
sub is_op_j { my $l = shift; return $l =~ /^\s*[jJ]\s*$/; }
sub is_op_p { my $l = shift; return $l =~ /^\s*[pP]\s*$/; }

sub state_g0 { my $l = shift; $state{g} = 0; }
sub state_g1 { my $l = shift; $state{g} = 1; }
sub state_g2 { my $l = shift; $state{g} = 2; }
sub state_g3 { my $l = shift; $state{g} = 3; }

sub state_f
{
  my $f = shift;
  print $FH_OUT "f$f";
}

sub state_s
{
  my $s = shift;
  print $FH_OUT "s$s";
}


sub state_g
{
  my $g = shift;
  $state{g} = $g;

  print $FH_OUT "g$g";
}

sub state_m
{
  my $m = shift;
  print $FH_OUT "m$m";
}

sub state_i
{
  my $i = shift;
  print $FH_OUT "i", sprintf("%4.8f", $x_scale*$i) ;
}

sub state_j
{
  my $j = shift;
  print $FH_OUT "j", sprintf("%4.8f", $y_scale*$j) ;
}

sub state_p
{
  my $p = shift;
  print $FH_OUT "p$p";
}

sub state_x
{
  my $x = shift;

  my $prev_dir = $state{x_dir};

  $state{x_dir} = ( ($x > $state{x}) ? 1 : -1 ) if (defined($state{x}));
  $state{prev_x} = $state{x};
  $state{x} = $x;

  print $FH_OUT " x", sprintf("%4.8f", $x_scale*($x)) ;
}

sub state_y
{
  my $y = shift;

  my $prev_dir = $state{y_dir};

  $state{y_dir} = ( ($y > $state{y}) ? 1 : -1 ) if (defined($state{y}));
  $state{prev_y} = $state{y};
  $state{y} = $y;

  print $FH_OUT " y", sprintf("%4.8f", $y_scale*($y)) ;
}


sub state_z
{
  my $z = shift;

  my $prev_dir = $state{z_dir};

  $state{z_dir} = ( ($z > $state{z}) ? 1 : -1 ) if (defined($state{z}));
  $state{prev_z} = $state{z};
  $state{z} = $z;

  print $FH_OUT "z", sprintf("%4.8f", $z_scale*($z)) ;
}
