#!/usr/bin/perl
#
# preload x and y positions for feed motions
#

use strict;
use Getopt::Std;
use Math::Trig;


$Getopt::Std::STANDARD_HELP_VERSION = 1;

my $VERSION_STR = "0.1 alpha";

sub VERSION_MESSAGE {
  print "ngc_rotate version ", $VERSION_STR, "\n"
}

sub usage
{
  print "usage:\n";
  print " [-f inp]              input gcode file (defaults to stdin)\n";
  print " [-o out]              output gcode file (defaults to stdout)\n";
  print " [-d deg]              rotation in degrees\n";
  print " [-r rad]              rotation in radians (overrides -d)\n";
  print " [-C]                  print comment header in output ngc (GRBL style)\n";
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
getopts("f:o:r:d:hC", \%opts);

my $rot_rad = 0.0;

my $COMMENT_JUST_PRINTED = 0;

if (exists($opts{h})) { usage(); exit; }
open($FH_INP, $opts{f}) if ($opts{f});
open($FH_OUT, ">$opts{o}") if ($opts{o});
$rot_rad = deg2rad($opts{d})  if ($opts{d});
$rot_rad = $opts{r}           if ($opts{r});

my $show_comments = 0;
if (exists($opts{C})) { $show_comments=1; }

my %rot_mat;
$rot_mat{"0,0"} =  cos($rot_rad);
$rot_mat{"0,1"} = -sin($rot_rad);
$rot_mat{"1,0"} =  sin($rot_rad);
$rot_mat{"1,1"} =  cos($rot_rad);

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

# transformed position
$state{x_t} = undef;
$state{prev_x_t} = undef;
$state{y_t} = undef;
$state{prev_y_t} = undef;
$state{z_t} = undef;
$state{prev_z_t} = undef;


$state{del_x} = 1;
$state{del_y} = 1;
$state{del_z} = 1;

$state{z_up}  = 1;

$state{x_dir} = 0;
$state{y_dir} = 0;
$state{z_dir} = 0;


$state{line_flag} = "";

my $op;
my $operand;

if ($show_comments) {
  print $FH_OUT "( rot_rad $rot_rad, rot_mat[ [ ", $rot_mat{"0,0"}, ", ", $rot_mat{"0,1"}, " ], [ ", $rot_mat{"1,0"}, ", ", $rot_mat{"1,1"}, " ] ] )\n";
}

foreach my $line (@gcode)
{
  chomp($line);
  $state{line_no}++;
  $state{line_flag} = "";
  $state{i} = 0.0;
  $state{j} = 0.0;

  if ( ($line =~ /^\s*;/) or
       ($line =~ /^\s*$/) )
  {
    print $FH_OUT $line, "\n";
    next;
  }

  $COMMENT_JUST_PRINTED = 0;
  my $tokens_processed = 0;

  while ($line)
  {

    if ($line =~ /^\s*$/)
    {
      $line = "";
      next;
    }

    $tokens_processed++;

    # print comment
    if (is_comment($line))
    {
      ($op, $line) = chomp_comment($line);

      # unfortunately we have to mangle the comment formatting
      # because we process commands at different points.
      # To be safe, put comments on their own isolated lines.
      # It gets a little ugly, but that's the price you pay for
      # simplicity and consistency
      print $FH_OUT "\n", $op, "\n";

      $COMMENT_JUST_PRINTED = 1;
      next;
    }

    $COMMENT_JUST_PRINTED = 0;

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

  print_command();

  print $FH_OUT "\n" ;

}
close $FH_OUT if fileno $FH_OUT != fileno STDOUT;

sub is_comment
{
  my $l = shift;

  $state{line_flag} .= ":comment";

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
  $state{f} = $f;

  $state{line_flag} .= ":f";
}

sub state_s
{
  my $s = shift;
  $state{s} = $s;

  $state{line_flag} .= ":s";
}


sub state_g
{
  my $g = shift;
  $state{g} = $g;

  $state{line_flag} .= ":g";
}


sub state_m
{
  my $m = shift;
  $state{m} = $m;

  $state{line_flag} .= ":m";
}

sub state_i
{
  my $i = shift;
  $state{i} = $i;

  $state{line_flag} .= ":i";
}

sub state_j
{
  my $j = shift;
  $state{j} = $j;

  $state{line_flag} .= ":j";
}

sub state_p
{
  my $p = shift;
  $state{p} = $p;

  $state{line_flag} .= ":p";
}

sub state_x
{
  my $x = shift;

  my $prev_dir = $state{x_dir};

  $state{x_dir} = ( ($x > $state{x}) ? 1 : -1 ) if (defined($state{x}));
  $state{prev_x} = $state{x};
  $state{x} = $x;

  $state{line_flag} .= ":x";
}

sub state_y
{
  my $y = shift;

  my $prev_dir = $state{y_dir};

  $state{y_dir} = ( ($y > $state{y}) ? 1 : -1 ) if (defined($state{y}));
  $state{prev_y} = $state{y};
  $state{y} = $y;

  $state{line_flag} .= ":y";
}

sub state_z
{
  my $z = shift;

  my $prev_dir = $state{z_dir};

  $state{z_dir} = ( ($z > $state{z}) ? 1 : -1 ) if (defined($state{z}));
  $state{prev_z} = $state{z};
  $state{z} = $z;

  $state{line_flag} .= ":z";
}


sub print_command
{

  print $FH_OUT "g", $state{g} if ($state{line_flag} =~ m/:[gG]/);

  if ($state{line_flag} =~ m/:[xyzijpXYZIJP]/)
  {

    # we must print both x and y out, might as well print z (might rotate in future)
    my ($x_r, $y_r, $z_r) = rot($state{x}, $state{y}, $state{z});

    # but only print it out if it's changed
    if ( ($state{line_flag} =~ /:[xX]/) or 
         ( defined($state{x_t}) and 
           $x_r != $state{x_t} ) )
    {
      print $FH_OUT " x", sprintf("%4.8f", $x_r) 
    }

    if ( ($state{line_flag} =~ /:[yY]/) or 
         ( defined($state{y_t}) and 
           $y_r != $state{y_t} ) )
    {
      print $FH_OUT " y", sprintf("%4.8f", $y_r) 
    }

    if ( ($state{line_flag} =~ /:[zZ]/) or 
         ( defined($state{z_t}) and 
           $z_r != $state{z_t} ) )
    {
      print $FH_OUT " z", sprintf("%4.8f", $z_r) 
    }

    $state{prev_x_t} = $state{x_t};
    $state{x_t} = $x_r;
    $state{prev_y_t} = $state{y_t};
    $state{y_t} = $y_r;
    $state{prev_z_t} = $state{z_t};
    $state{z_t} = $z_r;


    # rotate i and j by appropriate amount
    if ($state{line_flag} =~ m/:[ijIJ]/)
    {
      my ($i_r, $j_r, $dummy) = rot($state{i}, $state{j}, 0.0);
      print $FH_OUT " i", sprintf("%4.8f", $i_r),  " j", sprintf("%4.8f", $j_r);
    }

    # p left unmolested
    print $FH_OUT " p", $state{p} if ($state{line_flag} =~ m/:[pP]/);
  }

  print $FH_OUT " f", $state{f} if ($state{line_flag} =~ m/:[fF]/);
  print $FH_OUT " s", $state{s} if ($state{line_flag} =~ m/:[sS]/);
  print $FH_OUT " m", $state{m} if ($state{line_flag} =~ m/:[mM]/);

}

sub rot
{
  my $x = shift;
  my $y = shift;
  my $z = shift;

  my $x_new = $x * $rot_mat{"0,0"} + $y * $rot_mat{"0,1"};
  my $y_new = $x * $rot_mat{"1,0"} + $y * $rot_mat{"1,1"};

  return ($x_new, $y_new, $z);
}
