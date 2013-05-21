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
  print " [-x x]\n";
  print " [-y y]\n";
  print " [-z z]\n";
  print " [-s s]\n";
  print " [-h]                  help (this screen)\n";
}

open(my $fh_inp, "-");
open(my $fh_out, ">-");
my %opts;
getopts("f:o:x:y:z:s:h", \%opts);

my $x_shift = 0.0;
my $y_shift = 0.0;
my $z_shift = 0.0;
my $s_scale = 1.0;

if (exists($opts{h})) { usage(); exit; }
open($fh_inp, $opts{f}) if ($opts{f});
open($fh_out, ">$opts{o}") if ($opts{o});
$x_shift = $opts{x} if ($opts{x});
$y_shift = $opts{y} if ($opts{y});
$z_shift = $opts{z} if ($opts{z});
$s_scale = $opts{s} if ($opts{s});

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

print "( x_shift $x_shift, y_shift $y_shift, z_shift $z_shift, s_scale $s_scale )\n";

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
  print $fh_out "\n";

}
close $fh_out if fileno $fh_out != fileno STDOUT;

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
  print "f$f\n";
}

sub state_s
{
  my $s = shift;
  print "s$s\n";
}


sub state_g
{
  my $g = shift;
  $state{g} = $g;

  print "g$g\n";
}

sub state_m
{
  my $m = shift;
  print "m$m\n";
}

sub state_i
{
  my $i = shift;
  print "i", $s_scale*$i, "\n";
}

sub state_j
{
  my $j = shift;
  print "j", $s_scale*$j, "\n";
}

sub state_p
{
  my $p = shift;
  print "p$p\n";
}

sub state_x 
{
  my $x = shift;

  my $prev_dir = $state{x_dir};

  $state{x_dir} = ( ($x > $state{x}) ? 1 : -1 ) if (defined($state{x}));
  $state{prev_x} = $state{x};
  $state{x} = $x;

  #print "x", ($s_scale*($x + $x_shift)), "\n";
  print " x", ($s_scale*($x + $x_shift));
}

sub state_y
{
  my $y = shift;

  my $prev_dir = $state{y_dir};

  $state{y_dir} = ( ($y > $state{y}) ? 1 : -1 ) if (defined($state{y}));
  $state{prev_y} = $state{y};
  $state{y} = $y;

  print " y", ($s_scale*($y + $y_shift)), "\n";
}

sub state_z
{
  my $z = shift;

  my $prev_dir = $state{z_dir};

  $state{z_dir} = ( ($z > $state{z}) ? 1 : -1 ) if (defined($state{z}));
  $state{prev_z} = $state{z};
  $state{z} = $z;

  print "z", ($s_scale*($z + $z_shift)), "\n";
}


