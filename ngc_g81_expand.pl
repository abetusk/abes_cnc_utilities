#!/usr/bin/perl
#
#

use strict;

my $g81_state = 0;

my $feed = undef;
my $retract;
my $x;
my $y;
my $z;

while (<>)
{
  my $l = $_;

  if ($l =~ m/[gG]\s*8\s*1/)
  {

    if ($l =~ m/[fF](\d+(\.\d+)?)/)
    {
      $feed = $1;
    }

    if ($l =~ m/[rR](-?\d+(\.\d+)?)/)
    {
      $retract = $1;
    }
    else 
    {
      die "no retract";
    }

    if ($l =~ m/[xX](-?\d+(\.\d+)?)/)
    {
      $x = $1;
    }
    else {
      die "no X";
    }

    if ($l =~ m/[yY](-?\d+(\.\d+)?)/)
    {
      $y = $1
    }
    else {
      die "no Y";
    }

    if ($l =~ m/[zZ](-?\d+(\.\d+)?)/)
    {
      $z = $1;
    }
    else {
      die "no Z";
    }

    $g81_state = 1;

    print "g1 f$feed\n" if (defined $feed);
    print "g0 z$retract\n";
    print "g0 x${x}y$y\n";
    print "g1 z$z\n";
    print "g0 z$retract\n";
    print "\n";

  }
  elsif (!$g81_state)
  {
    print $l;
  }
  else
  {
    # in g81 state

    if ($l =~ m/^\s*$/)
    {
      $g81_state = 0;
      print $l;
    }
    else
    {
      if ($l =~ m/[xX](-?\d+(\.\d+)?)/)
      {
        $x = $1;
      }

      if ($l =~ m/[yY](-?\d+(\.\d+)?)/)
      {
        $y = $1
      }

      if ($l =~ m/[zZ](-?\d+(\.\d+)?)/)
      {
        $z = $1;
      }

      print "g0 z$retract\n";
      print "g0 x${x}y$y\n";
      print "g1 z$z\n";
      print "g0 z$retract\n";
      print "\n";
    }
  }

}
