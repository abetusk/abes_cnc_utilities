#!/usr/bin/perl
#

use strict;
use Getopt::Std;

sub usage
{
  print "usage:\n";
  print " [-f inp]          input gcode file (defaults to stdin)\n";
  print " [-o out]          output gcode file (defaults to stdout)\n";
  print " [-w min_width]    fit as many as you can within minimum width (default to 0) in mm\n";
  print " [-W max_width]    fit as many as you can within maximum width in mm\n";
  print " [-t min_height]   fit as many as you can within minimum height (default to 0) in mm\n";
  print " [-T max_height]   fit as many as you can within maximum height in mm\n";
  print " [-a hor_sep]      horizontal seperation between panels (defaults to 10mm) in mm\n";
  print " [-b ver_sep]      vertical seperation between panels (defaults to 10mm) in mm\n";
  print " [-c col]          create col columns \n";
  print " [-r row]          create row rows\n";
  print " [-D]              go down instead of up\n";
  print " [-L]              go left instead of right\n";
  print " [-h]              help (this screen)\n";
}

open(my $fh_inp, "-");
open(my $fh_out, ">-");
my %opts;
getopts("f:o:w:W:t:T:a:b:c:r:hDL", \%opts);

my $row_col_usage;
my $min_width = 0;
my $min_height = 0;
my $max_width = -1;
my $max_height = -1;

my $hori_sep = 10.0;
my $vert_sep = 10.0;

my $col = 1;
my $row = 1;

my $up_flag = 1;
my $right_flag = 1;

if (exists($opts{h})) { usage(); exit; }
open($fh_inp, $opts{f}) if ($opts{f});
open($fh_out, ">$opts{o}") if ($opts{o});
$min_width = $opts{w} if ($opts{w});
$max_width = $opts{W} if ($opts{W});
$min_height = $opts{t} if ($opts{t});
$max_height = $opts{T} if ($opts{T});
$col = $opts{c} if ($opts{c});
$row = $opts{r} if ($opts{r});
$up_flag = 0 if ($opts{D});
$right_flag = 0 if ($opts{L});

$hori_sep = $opts{a} if ($opts{a});
$vert_sep = $opts{b} if ($opts{b});

die "horizontal seperation must be positive ($hori_sep)" if ($hori_sep < 0.0);
die "vertical seperation must be positive ($vert_sep)" if ($vert_sep < 0.0);

if ( ($row >= 1) and ($col >= 1) )
{
  $row_col_usage = 1;
  #...
}
else
{
  $row_col_usage = 0;
  die "width error ($min_width > $max_width)" if ($min_width > $max_width);
  die "height error ($min_height > $max_height)" if ($min_height > $max_height);
  die "width error ($min_width > $max_width)" if ($min_width > $max_width);
  die "height error ($min_height > $max_height)" if ($min_height > $max_height);
}

print ";row $row, col $col, min_width $min_width, min_height $min_height, max_width $max_width, max_height $max_height\n";
print ";hori_sep $hori_sep\n";
print ";vert_sep $vert_sep\n";

# read in gcode
my @gcode;
while (<$fh_inp>)
{
  push @gcode, $_;
}
close $fh_inp if fileno $fh_inp != fileno STDIN;


# get bounds
my @r = get_bounds(\@gcode);
die "imporoper bounds for gcode file" if (scalar(@r) == 0);
my ($x_min, $x_max, $y_min, $y_max, $z_min, $z_max) = @r;

my $dx = $x_max - $x_min;
my $dy = $y_max - $y_min;

print ";bounds:\n";
print ";x_min: $x_min\n";
print ";x_max: $x_max\n";

print ";y_min: $y_min\n";
print ";y_max: $y_max\n";

print ";z_min: $z_min\n";
print ";z_max: $z_max\n";

# panalize simple
for (my $r = 0; $r < $row; $r++)
{
  for (my $c = 0; $c < $col; $c++)
  {

    if ( ( $r == 0 ) and ( $c == 0 ) )
    {
      for (my $line_no; $line_no < scalar(@gcode); $line_no++)
      {
        my $l = $gcode[$line_no];
        $l =~ s/[mM]2//g;
        $l =~ s/[mM]30//g;
        print $fh_out $l;
        #print $fh_out $gcode[$line_no];
      }
      next;
    }

    my $shift_x = ($c * ($dx + $hori_sep));
    my $shift_y = ($r * ($dx + $vert_sep));

    $shift_x *= -1.0 if (!$right_flag);
    $shift_y *= -1.0 if (!$up_flag);

    plot_shift($fh_out, \@gcode, $shift_x, $shift_y);

    print ";------------------------\n";

  }
}



close $fh_out if fileno $fh_out != fileno STDOUT;

sub plot_shift
{
  my $fh_out = shift;
  my $gcode = shift;
  my $shift_x = shift;
  my $shift_y = shift;

  my $is_mm = 1;

  for (my $line_no=0; $line_no<scalar(@$gcode); $line_no++)
  {
    my $l = $gcode->[$line_no];

    # take out comments
    $l =~ s/;.*//;
    $l =~ s/\([^)]*\)//g;

    # get rid of end program directive
    $l =~ s/[mM]2//g;
    $l =~ s/[mM]30//g;

    my $matching = 1;

    my $g_line = $l;
    while ($matching)
    {
      $matching = 0;

      my $match_unit_pos = -1;
      my $match_axis_pos = -1;

      $match_unit_pos = @+[0] if ($g_line =~ /[gG]\s*2([01])/);
      $match_axis_pos = @+[0] if ($g_line =~ /[xXyY]\s*(-?\s*\d+(\.\d+)?)/);

      if    ( ($match_unit_pos >= 0) and
              ( ($match_axis_pos == -1) or
                ($match_unit_pos < $match_axis_pos) ) )
      {
        $g_line =~ /[gG]\s*2([01])/;
        my ($s, $e) = ( @-[0], @+[0] );

        my $zo = $1;
        $is_mm = 0 if ($zo eq "0");
        $is_mm = 1 if ($zo eq "1");

        print substr $g_line, 0, $s;
        print "g2$zo";

        $g_line = substr $g_line, $e;
        $matching = 1;
      }
      elsif ( ($match_axis_pos >= 0) and
              ( ($match_unit_pos == -1) or
                ($match_unit_pos < $match_axis_pos) ) )
      {
        $g_line =~ /([xXyY])\s*(-?\s*\d+(\.\d+)?)/;
        my ($axis, $val) = ($1, $2);
        my ($s, $e) = ( @-[0], @+[0] );

        my $val_mm = ( $is_mm ? $val : ($val * 25.4) );

        $val_mm += $shift_x if ($axis =~ /[xX]/);
        $val_mm += $shift_y if ($axis =~ /[yY]/);

        my $val_print = ( $is_mm ? $val_mm : ($val_mm / 25.4) );

        print substr $g_line, 0, $s;
        print "$axis$val_print";

        $g_line = substr $g_line, $e;
        $matching = 1;

      }
    }

    print $g_line;

  }

}


sub get_bounds
{
  my $gcode = shift;

  my $n = scalar(@$gcode);

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


  for (my $i=0; $i<$n; $i++)
  {
    my $l = $gcode->[$i];

    # take out comments
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
        $x_min_mm = $is_mm ;
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

  undef if ( not $have_x or not $have_y or not $have_z );

  return ($x_min_mm, $x_max_mm, $y_min_mm, $y_max_mm, $z_min_mm, $z_max_mm);

}
