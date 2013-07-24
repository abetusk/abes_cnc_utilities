#!/usr/bin/perl
#
# preload x and y positions for feed motions
#

use strict;
use Getopt::Std;
use Math::Trig;

sub usage
{
  print "usage:\n";
  print " [-f inp]              input gcode file (defaults to stdin)\n";
  print " [-o out]              output gcode file (defaults to stdout)\n";
  print " [-d deg]              rotation in degrees\n";
  print " [-r rad]              rotation in radians\n";
  print " [-h]                  help (this screen)\n";
}

open(my $fh_inp, "-");
open(my $fh_out, ">-");
my %opts;
getopts("f:o:r:d:h", \%opts);

my $rot_rad = 0.0;


if (exists($opts{h})) { usage(); exit; }
open($fh_inp, $opts{f}) if ($opts{f});
open($fh_out, ">$opts{o}") if ($opts{o});
$rot_rad = deg2rad($opts{d})  if ($opts{d});
$rot_rad = $opts{r}           if ($opts{r});

my %rot_mat;
$rot_mat{"0,0"} =  cos($rot_rad);
$rot_mat{"0,1"} = -sin($rot_rad);
$rot_mat{"1,0"} =  sin($rot_rad);
$rot_mat{"1,1"} =  cos($rot_rad);

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


$state{line_flag} = "";

my $op;
my $operand;

#print "( x_shift $x_shift, y_shift $y_shift, z_shift $z_shift, s_scale $s_scale )\n";
print "( rot_rad $rot_rad, rot_mat[ [ ", $rot_mat{"0,0"}, ", ", $rot_mat{"0,1"}, " ], [ ", $rot_mat{"1,0"}, ", ", $rot_mat{"1,1"}, " ] ] )\n";

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

    print $fh_out $line, " ( unprocessed )\n";
    $line = '';

  }

  print_command();

  print $fh_out "\n";

}
close $fh_out if fileno $fh_out != fileno STDOUT;

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

  #print "f$f\n";
}

sub state_s
{
  my $s = shift;
  $state{s} = $s;

  $state{line_flag} .= ":s";

  #print "s$s\n";
}


sub state_g
{
  my $g = shift;
  $state{g} = $g;

  $state{line_flag} .= ":g";

  #print "g$g\n";
}


sub state_m
{
  my $m = shift;
  $state{m} = $m;

  $state{line_flag} .= ":m";

  #print "m$m\n";
}

sub state_i
{
  my $i = shift;
  $state{i} = $i;

  $state{line_flag} .= ":i";

  #print "i", $s_scale*$i, "\n";
}

sub state_j
{
  my $j = shift;
  $state{j} = $j;

  $state{line_flag} .= ":j";

  #print "j", $s_scale*$j, "\n";
}

sub state_p
{
  my $p = shift;
  $state{p} = $p;

  $state{line_flag} .= ":p";

  #print "p$p\n";
}

sub state_x
{
  my $x = shift;

  my $prev_dir = $state{x_dir};

  $state{x_dir} = ( ($x > $state{x}) ? 1 : -1 ) if (defined($state{x}));
  $state{prev_x} = $state{x};
  $state{x} = $x;

  $state{line_flag} .= ":x";

  #print " x", ($s_scale*($x + $x_shift));
}

sub state_y
{
  my $y = shift;

  my $prev_dir = $state{y_dir};

  $state{y_dir} = ( ($y > $state{y}) ? 1 : -1 ) if (defined($state{y}));
  $state{prev_y} = $state{y};
  $state{y} = $y;

  $state{line_flag} .= ":y";

  #print " y", ($s_scale*($y + $y_shift)), "\n";
}

sub state_z
{
  my $z = shift;

  my $prev_dir = $state{z_dir};

  $state{z_dir} = ( ($z > $state{z}) ? 1 : -1 ) if (defined($state{z}));
  $state{prev_z} = $state{z};
  $state{z} = $z;

  $state{line_flag} .= ":z";

  #print "z", ($s_scale*($z + $z_shift)), "\n";
}


sub print_command
{

  print "g", $state{g} if ($state{line_flag} =~ m/:[g]/);

  if ($state{line_flag} =~ m/:[xyzijp]/)
  {

    # we must print both x and y out, might as well print z (might rotate in future)
    my ($x_r, $y_r, $z_r) = rot($state{x}, $state{y}, $state{z});
    print " x", sprintf("%4.8f", $x_r), " y", sprintf("%4.8f", $y_r), " z", sprintf("%4.8f", $z_r);

    # rotate i and j by appropriate amount
    if ($state{line_flag} =~ m/:[ij]/)
    {
      my ($i_r, $j_r, $dummy) = rot($state{i}, $state{j}, 0.0);
      print " i", sprintf("%4.8f", $i_r),  " j", sprintf("%4.8f", $j_r);
    }

    # p left unmolested
    print " p", $state{p} if ($state{line_flag} =~ m/[p]/);
  }

  print " f", $state{f} if ($state{line_flag} =~ m/:[f]/);
  print " s", $state{f} if ($state{line_flag} =~ m/:[s]/);
  print " m", $state{f} if ($state{line_flag} =~ m/:[m]/);

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
