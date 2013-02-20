#!/usr/bin/perl
#

use strict;

my $fn = ($ARGV[0] || die "provide gcode file");
die "invalid file: $fn" if (!-e $fn);

# default to mm
my $is_mm = 1;

my $have_x = 0;
my $have_y = 0;
my $have_z = 0;

my $x_min_mm;
my $x_max_mm;

my $y_min_mm;
my $y_max_mm;

my $z_min_mm;
my $z_max_mm;


open FIL, $fn;
while (<FIL>)
{
  my $l = $_;

  $l =~ s/;.*//;
  $l =~ s/\([^)]*\)//g;

  my $g_line = $l;
  while ($g_line =~ /[gG]\s*2([01])/)
  {
    my $zo = $1;
    $is_mm = 0 if ($zo eq "0");
    $is_mm = 1 if ($zo eq "1");
    $g_line = substr $g_line, (@+[0]);
  }

  while ($g_line =~ /[xX]\s*(-?\d+(\.\d+)?)/)
  {
    my $x = $1;
    my $x_mm = ( $is_mm ? $x : ($x * 25.4) );
    if (!$have_x)
    {
      $x_min_mm = $x_mm;
      $x_max_mm = $x_min_mm;
      $have_x = 1;
    }
    else
    {
      $x_min_mm = $x_mm if ($x_min_mm > $x_mm);
      $x_max_mm = $x_mm if ($x_max_mm < $x_mm);
    }
    $g_line = substr $g_line, (@+[0]);
  }

  $g_line = $l;
  while ($g_line =~ /[yY]\s*(-?\d+(\.\d+)?)/)
  {
    my $y = $1;
    my $y_mm = ( $is_mm ? $y : ($y * 25.4) );
    if (!$have_y)
    {
      $y_min_mm = $y_mm;
      $y_max_mm = $y_min_mm;
      $have_y = 1;
    }
    else
    {
      $y_min_mm = $y_mm if ($y_min_mm > $y_mm);
      $y_max_mm = $y_mm if ($y_max_mm < $y_mm);
    }
    $g_line = substr $g_line, (@+[0]);
  }

  my $g_line = $l;
  while ($g_line =~ /[zZ]\s*(-?\d+(\.\d+)?)/)
  {
    my $z = $1;
    my $z_mm = ( $is_mm ? $z : ($z * 25.4) );
    if (!$have_z)
    {
      $z_min_mm = $z_mm;
      $z_max_mm = $z_min_mm;
      $have_z = 1;
    }
    else
    {
      $z_min_mm = $z_mm if ($z_min_mm > $z_mm);
      $z_max_mm = $z_mm if ($z_max_mm < $z_mm);
    }
    $g_line = substr $g_line, (@+[0]);
  }

}
close FIL;

die "don't have all of x, y, z co-ords" if ( not $have_x or not $have_y or not $have_z );

print "min_x: ", $x_min_mm, " mm, ", ($x_min_mm/25.4), " inch\n";
print "max_x: ", $x_max_mm, " mm, ", ($x_max_mm/25.4), " inch\n";

print "min_y: ", $y_min_mm, " mm, ", ($y_min_mm/25.4), " inch\n";
print "may_y: ", $y_max_mm, " mm, ", ($y_max_mm/25.4), " inch\n";

print "min_z: ", $z_min_mm, " mm, ", ($z_min_mm/25.4), " inch\n";
print "max_z: ", $z_max_mm, " mm, ", ($z_max_mm/25.4), " inch\n";


