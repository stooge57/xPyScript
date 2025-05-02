# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.8.1
# WARNING! All changes made in this file will be lost!

from PyQt6 import QtCore

qt_resource_data = b"\
\x00\x00\x16\x06\
<\
!--This file is \
under MIT licens\
e. The license f\
ile can be obtai\
ned in the root \
directory of thi\
s module.-->\x0d\x0a<!\
DOCTYPE html>\x0d\x0a<\
html>\x0d\x0a<head>\x0d\x0a \
 <style>\x0d\x0a    p \
{\x0d\x0a     word-wra\
p: break-word;\x0d\x0a\
     white-space\
: normal;\x0d\x0a    }\
\x0d\x0a\x0d\x0a    dd {\x0d\x0a  \
   margin-bottom\
: 10px;\x0d\x0a    }\x0d\x0a\
  </style>\x0d\x0a</he\
ad>\x0d\x0a<body>\x0d\x0a\x0d\x0a<\
h3>Introduction<\
/h3>\x0d\x0a<p>\x0d\x0axPySc\
ript is a free a\
nd open source p\
rogram that allo\
ws you to progra\
m single display\
 models\x0d\x0a using \
python.You speci\
fy a xLights xmo\
del that defines\
 the physical el\
ement of your di\
splay prop\x0d\x0a and\
 use Python to a\
nimate the light\
s, similar to us\
ing an Arduino a\
nd the FastLED l\
ibrary. Output\x0d\x0a\
 is to the scree\
n and the physic\
al LED pixels vi\
a a E1.31 contro\
ller if connecte\
d. Currently onl\
y\x0d\x0a 3 channel RG\
B pixels and E1.\
31 protocol cont\
rollers are supp\
orted. The resul\
tant sequence ca\
n be\x0d\x0a exported \
to an xlight's .\
xsq file, which \
can be opened by\
 xLights and add\
ed to a larger s\
equence\x0d\x0a or sav\
ed to a .fseq fi\
le.\x0d\x0a</p>\x0d\x0a\x0d\x0a<hr\
>\x0d\x0a<h3>Menu Comm\
ands</h3>\x0d\x0a<dt><\
i>New</i></dt>\x0d\x0a\
<dd>Creates a ne\
w sequence. This\
 creates a .xscr\
 file to save fi\
le settings and \
a .py file where\
\x0d\x0a the actual pr\
ogramming takes \
place.</dd>\x0d\x0a\x0d\x0a<\
dt><i>Export</i>\
</dt>\x0d\x0a<dd>Expor\
ts a sequence of\
 the specified l\
ength to an xLig\
hts .xsq file.</\
dd>\x0d\x0a\x0d\x0a<dt><i>Ru\
n</i></dt>\x0d\x0a<dd>\
Executes the seq\
uence's python p\
rogram. You can \
Stop the sequenc\
e, modify the co\
de\x0d\x0a (and save) \
and Run will rel\
oad the updated \
code without exi\
ting PyLights.</\
dd>\x0d\x0a\x0d\x0a<dt><i>St\
op</i></dt>\x0d\x0a<dd\
>Stops the seque\
nce's python pro\
gram.</dd>\x0d\x0a\x0d\x0a<d\
t><i>Node ID</i>\
</dt>\x0d\x0a<dd>Used \
to select and id\
entify the model\
's node numbers \
which simplifys \
making node list\
s\x0d\x0a for programm\
ing. Multiple No\
de mode allows n\
odes to be indiv\
idually selected\
 with the left\x0d\x0a\
 mouse button or\
 by holding down\
 the left mouse \
button and movin\
g the cursor ove\
r the nodes.\x0d\x0a T\
hey can be desel\
ected from the l\
ist by holding d\
own the ctrl but\
ton. The Window \
Node mode\x0d\x0a allo\
ws node selectio\
n by drawing win\
dows around the \
nodes. The resul\
tant list is sho\
wn in\x0d\x0a the stat\
us bar and is co\
pied automatical\
ly to the clipbo\
ard</dd>\x0d\x0a\x0d\x0a<dt>\
<i>Interactive C\
olor</i></dt>\x0d\x0a<\
dd>Shows how the\
 selected color \
will look on the\
 physical pixel.\
 The selected co\
lor is\x0d\x0a copied \
automatically to\
 the clipboard. \
Output to Lights\
 menu option has\
 to be enabled.<\
/dd>\x0d\x0a\x0d\x0a<dt><i>A\
pplication Setti\
ngs</i></dt>\x0d\x0a<d\
d>Application se\
ttings are optio\
ns applying to a\
ll files. Option\
s to customize s\
creen\x0d\x0a appearan\
ce and whether t\
o use unicast or\
 multicast E1.31\
.</dd>\x0d\x0a\x0d\x0a<dt><i\
>File Settings</\
i></dt>\x0d\x0a<dd>Fil\
e settings are o\
ptions applying \
only to the open\
ed file. The str\
etch option modi\
fies\x0d\x0a the aspec\
t ratio of the m\
odel's screen di\
splay. The Node \
Mapping is used \
to configure the\
\x0d\x0a universe/chan\
nel setup; these\
 settings must m\
atch the pixel c\
ontroller settin\
gs.</dd>\x0d\x0a\x0d\x0a<hr>\
\x0d\x0a<h3>Programmin\
g</h3>\x0d\x0aThe foll\
owing is the lis\
t of the standar\
d Sequence metho\
ds and attribute\
s. Some are used\
\x0d\x0a to access the\
 pixels' buffer \
while others are\
 useful convenie\
nce methods. The\
se are class\x0d\x0a m\
ethods/attribute\
s, so they need \
to be prefixed b\
y self. Any Pyth\
on methods and m\
odules can be us\
ed.\x0d\x0a The setup(\
) method is call\
ed just once, so\
 initialization \
and defining pro\
gram variables i\
s done \x0d\x0ahere. T\
he loop() method\
 is where we wri\
te the code that\
 we want to exec\
ute over and \x0d\x0ao\
ver again.<br><b\
r>\x0d\x0a\x0d\x0a<dt><i>cho\
ice(list)</i></d\
t>\x0d\x0a<dd>Returns \
a randomly selec\
ted element from\
 the argument li\
st.</dd>\x0d\x0a\x0d\x0a<dt>\
<i>clear(nodeNum\
bers)</i></dt>\x0d\x0a\
<dd>Clears the n\
odes given in th\
e nodeNumbers li\
st. Argument can\
 also be a singl\
e integer.</dd>\x0d\
\x0a\x0d\x0a<dt><i>clearA\
ll()</i></dt>\x0d\x0a<\
dd>Clears the en\
tire model.</dd>\
\x0d\x0a\x0d\x0a<dt><i>delay\
(ms)</i></dt>\x0d\x0a<\
dd>Pauses the se\
quence for the s\
pecified period \
in milliseconds.\
</dd>\x0d\x0a\x0d\x0a<dt><i>\
doEveryMillis(id\
Key, N)</i></dt>\
\x0d\x0a<dd>Executes t\
he following blo\
ck of code every\
 N milliseconds.\
 Give each insta\
nce a unique idK\
ey.</dd>\x0d\x0a\x0d\x0a<dt>\
<i>doEverySecond\
s(idKey, N)</i><\
/dt>\x0d\x0a<dd>Execut\
es the following\
 block of code e\
very N seconds. \
Give each instan\
ce a unique idKe\
y.</dd>\x0d\x0a\x0d\x0a<dt><\
i>random(max)</i\
></dt>\x0d\x0a<dd>Retu\
rns a random num\
ber between 0 an\
d max-1.</dd>\x0d\x0a\x0d\
\x0a<dt><i>randomRa\
nge(min, max)</i\
></dt>\x0d\x0a<dd>Retu\
rns a random num\
ber between min \
and max-1.</dd>\x0d\
\x0a\x0d\x0a<dt><i>setHsv\
(nNodeNumbers, h\
ue, saturation, \
value)</i></dt>\x0d\
\x0a<dd>Sets the li\
st of nodes to t\
he HSV color. Hu\
e is between 0 a\
nd 359,\x0d\x0a satura\
tion and value a\
re between 0 and\
 255. List argum\
ent can also be \
a single integer\
.</dd>\x0d\x0a\x0d\x0a<dt><i\
>setHsvAll(hue, \
saturation, valu\
e)</i></dt>\x0d\x0a<dd\
>Sets the entire\
 model to the HS\
V color. Hue is \
between 0 and 35\
9,\x0d\x0a saturation \
and value are be\
tween 0 and 255.\
</dd>\x0d\x0a\x0d\x0a<dt><i>\
setMasterBrightn\
ess(scale)</i></\
dt>\x0d\x0a<dd>Sets th\
e overall bright\
ness of the mode\
l. Scale is betw\
een 0.0 and 1.0.\
</dd>\x0d\x0a\x0d\x0a<dt><i>\
setRgb(nNodeNumb\
ers, rgb)</i></d\
t>\x0d\x0a<dd>Sets the\
 list of nodes t\
o the 32-bit rgb\
 argument color.\
 List argument c\
an also be a\x0d\x0a s\
ingle integer.</\
dd>\x0d\x0a\x0d\x0a<dt><i>se\
tRgbAll(rgb)</i>\
</dt>\x0d\x0a<dd>Sets \
the entire model\
 to the 32-bit r\
gb argument colo\
r.</dd>\x0d\x0a\x0d\x0a<dt><\
i>setRgb3(nNodeN\
umbers, red, gre\
en, blue)</i></d\
t>\x0d\x0a<dd>Sets the\
 list of nodes t\
o the red/green/\
blue argument co\
lor. List argume\
nt can also\x0d\x0a be\
 a single intege\
r.</dd>\x0d\x0a\x0d\x0a<dt><\
i>setRgb3All(nNo\
deNumbers, red, \
green, blue)</i>\
</dt>\x0d\x0a<dd>Sets \
the entire model\
 to the red/gree\
n/blue argument \
color.</dd>\x0d\x0a\x0d\x0a<\
dt><i>show()</i>\
</dt>\x0d\x0a<dd>Sends\
 the color data \
stored in the pi\
xels buffer to t\
he screen and ph\
ysical LED strin\
gs.</dd>\x0d\x0a\x0d\x0a<dt>\
<i>nNodes [attri\
bute]</i></dt>\x0d\x0a\
<dd>The number o\
f nodes in the m\
odel.</dd>\x0d\x0a\x0d\x0a<d\
t><i>nodeColors \
[attribute]</i><\
/dt>\x0d\x0a<dd>A list\
 of the current \
node colors (QCo\
lor) of the mode\
l.</dd><br>\x0d\x0a\x0d\x0a<\
/body>\x0d\x0a</html>\x0d\
\x0a\x0d\x0a\x0d\x0a\
"

qt_resource_name = b"\
\x00\x12\
\x0edG<\
\x00x\
\x00P\x00y\x00S\x00c\x00r\x00i\x00p\x00t\x00H\x00e\x00l\x00p\x00.\x00h\x00t\x00m\
\x00l\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x96{\xf0\xaa\x22\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
