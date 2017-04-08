// units in mm

width_foundation = 50;
width_extra = 6*2;

x_size = width_foundation + width_extra;
y_size = 20;

center_x = x_size/2;
center_y = y_size/2;

join_hole_x = x_size/2 - y_size/2;
join_hole_y = y_size/2;

join_hole_r = 3.5/2;

pb_hole_dist = 6.3;
pb_hole_cent_y = pb_hole_dist/2;
pb_hole_cent_x = width_foundation/2 + width_extra/4;
pb_hole_r = 2/2;

difference() {
  square([x_size,y_size], true);
  translate([join_hole_x, 0])
    circle(join_hole_r, $fn=20);
  translate([-join_hole_x,0])
    circle(join_hole_r, $fn=20);
  
  translate([pb_hole_cent_x,pb_hole_cent_y])
    circle(pb_hole_r, $fn=20);
  translate([pb_hole_cent_x,-pb_hole_cent_y])
    circle(pb_hole_r, $fn=20);
  
  translate([-pb_hole_cent_x,pb_hole_cent_y])
    circle(pb_hole_r, $fn=20);
  translate([-pb_hole_cent_x,-pb_hole_cent_y])
    circle(pb_hole_r, $fn=20);
}