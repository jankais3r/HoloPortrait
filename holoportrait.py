import io
import os
import sys
import json
import time
import Image
import numpy
import base64
import photos
import urllib.parse
from ui import WebView
from objc_util import *
from math import atan, cos, floor

# Get your calibration values at https://eka.hn/calibration_test.html
config_json = '''
{
	"configVersion": "1.0",
	"serial": "LKG-2K-04409",
	"pitch": {"value": 47.56401443481445},
	"slope": {"value": -5.480000019073486},
	"center": {"value": 0.374184787273407},
	"viewCone": {"value": 40.0},
	"invView": {"value": 1.0},
	"verticalAngle": {"value": 0.0},
	"DPI": {"value": 338.0},
	"screenW": {"value": 2560.0},
	"screenH": {"value": 1600.0},
	"flipImageX": {"value": 0.0},
	"flipImageY": {"value": 0.0},
	"flipSubp": {"value": 0.0}
}
'''
debug = False

# This delegate allows us to talk from the WebView back to Python.
class debugDelegate(object):
	def webview_should_start_load(self, webview, url, nav_type):
		global done
		if url == 'ios-log:done':
			print('')
			v.close()
			done = True
		elif url.startswith('ios-log:data:image/png;base64'):
			message = urllib.parse.unquote(url)
			clean = message[30:]
			decoded = base64.b64decode(clean)
			stream = io.BytesIO(decoded)
			img = Image.open(stream)
			counter = len(quiltImages)
			
			# This shifts the starting horizontal position of individual views in order to keep the objects fixed in their perceived location.
			if debug == True:
				img_centered = Image.new('RGB', (980, 961), (255, 255, 255))
				img_centered.paste(img, (counter * 15 - 330, 0))
				img_centered.show()
			else:
				img_centered = Image.new('RGB', (980, 961))
				img_centered.paste(img, (counter * 15 - 330, 0))
			quiltImages.append(img_centered)
			print('|', end ='')
		return True
	
	def webview_did_finish_load(self, webview):
		print('Step 3/6 - Capturing 45 views ', end ='')
		pass

# This class uses iOS API to fetch a depth map from the provided image data. The beauty of it is that it works regardless if we have a JPG or a HEIC file.
class CImage(object):
	def __init__(self, chosen_pic_data):
		CIImage = ObjCClass('CIImage')
		options = {}
		options['kCIImageAuxiliaryDepth'] = ns(True)
		options['kCIImageApplyOrientationProperty'] = ns(True)
		self.ci_img = CIImage.imageWithData_options_(chosen_pic_data, options)
	
	def to_png(self):
		ctx = ObjCClass('CIContext').context()
		try:
			extent = self.ci_img.extent()
		except:
			print('The selected portrait photo does not contain a depth map.')
			quit()
		m = ctx.outputImageMaximumSize()
		cg_img = ctx.createCGImage_fromRect_(self.ci_img, extent)
		ui_img = UIImage.imageWithCGImage_(cg_img)
		png_data = uiimage_to_png(ObjCInstance(ui_img))
		return png_data

quiltImages = []
done = False

# This might break on non-English iOS. Too lazy to test.
for album in photos.get_smart_albums():
	if album.title == 'Portrait':
		my_album = album
		break

# Again using iOS API to get the photo's proper filename
try:
	chosen_pic = photos.pick_asset(assets = my_album.assets, title = 'Select a portrait photo')
	filename, file_extension = os.path.splitext(str(ObjCInstance(chosen_pic).originalFilename()))
	assert filename != 'None'
	output_filename = 'Holo_' + filename + '.png'
except:
	quit()

print('Step 1/6 - Extracting a depth map')
chosen_pic_image = chosen_pic.get_image(original = True)
chosen_pic_data = chosen_pic.get_image_data(original = True).getvalue()

chosen_pic_depth = CImage(ns(chosen_pic_data)).to_png()
chosen_pic_depth_stream = io.BytesIO(chosen_pic_depth)
chosen_pic_depth_image = Image.open(chosen_pic_depth_stream)

arr = numpy.array(chosen_pic_depth_image).astype(int)

# Some Portrait photos have a completely white depth map. Let's treat those as if there was no depth map at all.
if numpy.ptp(arr) == 0:
		print('The selected portrait photo does not contain a depth map.')
		quit()

# This part takes the depth map and normalizes its values to the range of (0, 110). You can experiment with the value, 255 is the ceiling.
chosen_pic_depth_image_array = (110*(arr - numpy.min(arr))/numpy.ptp(arr)).astype(int)
chosen_pic_depth_image = Image.fromarray(numpy.uint8(chosen_pic_depth_image_array))

# Making the images smaller for faster processing.
chosen_pic_image.thumbnail((800, 800), Image.ANTIALIAS)
chosen_pic_depth_image.thumbnail((800, 800), Image.ANTIALIAS)

# Turning the images into a base64 blob that can be used in the three.js scene
chosen_pic_image_buffer = io.BytesIO()
chosen_pic_image.save(chosen_pic_image_buffer, format = 'PNG')
rgbData = 'data:image/png;base64,' + base64.b64encode(chosen_pic_image_buffer.getvalue()).decode('utf-8')
chosen_pic_depth_image_buffer = io.BytesIO()
chosen_pic_depth_image.save(chosen_pic_depth_image_buffer, format = 'PNG')
depthData = 'data:image/png;base64,' + base64.b64encode(chosen_pic_depth_image_buffer.getvalue()).decode('utf-8')

html = '''
<html>
<head>
<style>
body {
	margin: 0;
}
canvas {
	width: 100vw;
	height: 100vh;
	display: block;
}
</style>
<script src="https://threejsfundamentals.org/threejs/resources/threejs/r94/three.min.js"></script>
</head>
<body>
<canvas></canvas>
<script>
js2py = new Object();
js2py.send = function(log) {
	// Create an iframe to communicate with the webview delegate, then remove it.
	var iframe = document.createElement("IFRAME");
	iframe.setAttribute("src", "ios-log:" + log);
	document.documentElement.appendChild(iframe);
	iframe.parentNode.removeChild(iframe);
	iframe = null;
};

'use strict';
function loadImage(url) {
	return new Promise((resolve, reject) => {
		const img = new Image();
		img.crossOrigin = "anonymous";
		img.onload = (e) => { resolve(img); };
		img.onerror = reject;
		img.src = url;
	});
}

function getImageData(img) {
	const ctx = document.createElement("canvas").getContext("2d");
	ctx.canvas.width = img.width;
	ctx.canvas.height = img.height;
	ctx.drawImage(img, 0, 0);
	return ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
}

function getPixel(imageData, u, v) {
	const x = u * (imageData.width - 1) | 0;
	const y = v * (imageData.height - 1) | 0;
	if (x < 0 || x >= imageData.width || y < 0 || y >= imageData.height) {
		return [0, 0, 0, 0];
	} else {
		const offset = (y * imageData.width + x) * 4;
		return Array.from(imageData.data.slice(offset, offset + 4)).map(v => v / 255);
	}
}

async function main() {
	const images = await Promise.all([
		loadImage("''' + rgbData + '''"), // RGB
		loadImage("''' + depthData + '''"), // Depth
	]);
	const data = images.map(getImageData);
	
	const canvas = document.querySelector('canvas');
	const renderer = new THREE.WebGLRenderer({canvas: canvas,
	preserveDrawingBuffer: true});
	
	// Constants you can experiment with: near, far, camera.position.z, depthSpread, skip, size
	const fov = 70;
	const aspect = 2;
	const near = 1;
	const far = 4000;
	const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
	camera.position.z = 3400;
	
	const scene = new THREE.Scene();
	const rgbData = data[0];
	const depthData = data[1];
	
	const skip = 1;
	const across = Math.ceil(rgbData.width / skip);
	const down = Math.ceil(rgbData.height / skip);
	
	const positions = [];
	const colors = [];
	const color = new THREE.Color();
	const spread = 1000;
	const depthSpread = 1900;
	const imageAspect = rgbData.width / rgbData.height;
	const size = 10;
	
	for (let y = 0; y < down; ++y) {
		const v = y / (down - 1);
		for (let x = 0; x < across; ++x) {
			const u = x / (across - 1);
			const rgb = getPixel(rgbData, u, v);
			const depth = 1 - getPixel(depthData, u, v)[0];
			
			positions.push( 
				 (u * 2 - 1) * spread * imageAspect,
				 (v * -2 + 1) * spread, 
				 depth * depthSpread,
			);
			colors.push( ...rgb.slice(0,3) );
		}
	}
	
	const geometry = new THREE.BufferGeometry();
	geometry.addAttribute( 'position', new THREE.Float32BufferAttribute( positions, 3 ) );
	geometry.addAttribute( 'color', new THREE.Float32BufferAttribute( colors, 3 ) );
	geometry.computeBoundingSphere();
	const material = new THREE.PointsMaterial( { size: size, vertexColors: THREE.VertexColors } );
	const points = new THREE.Points( geometry, material );
	scene.add( points );
	
	function resizeRendererToDisplaySize(renderer) {
		const canvas = renderer.domElement;
		const width = canvas.clientWidth;
		const height = canvas.clientHeight;
		const needResize = canvas.width !== width || canvas.height !== height;
		if (needResize) {
			renderer.setSize(width, height, false);
		}
		return needResize;
	}
	
	function render(time) {
		time *= 0.001;
		
		if (resizeRendererToDisplaySize(renderer)) {
			const canvas = renderer.domElement;
			camera.aspect = canvas.clientWidth / canvas.clientHeight;
			camera.updateProjectionMatrix();
		}
		
		// This part takes care of taking picture from 45 linear views. If you experiment with the movement, don't forget to adjust the shift on rows 55 & 59.
		camera.position.x = -900;
		for (i = 0; i < 45; i++) { 
			camera.position.x += 40;
			renderer.render(scene, camera);
			js2py.send(renderer.domElement.toDataURL('image/png'));
		}
		js2py.send('done');
	}
	requestAnimationFrame(render);
}
main();
</script>
</body>
</html>
'''

# Create a WebView that will be used to render the three.js scene, and make it hidden.
v = WebView()
v.delegate = debugDelegate()
v.hidden = True
v.present(hide_title_bar = True)

# This is a default size of the view on an iPad, but we need to hardcode it otherwise the thing falls apart when run on an iPhone.
v.width = 704
v.height = 690
v.load_html(html)
print('Step 2/6 - Rendering a point cloud')

# Wait until the JavaScript sends us a signal that it finished rendering the views.
while done != True:
	time.sleep(1)

print('Step 4/6 - Combining the views into a quilt')
dst = Image.new('RGB', (4096, 4096))

# A very low-tech approach to defining a position of each view on a quilt.
w = 819
h = 455
order = {
	1 : (w*0, h*8+1), 2 : (w*1, h*8+1), 3 : (w*2, h*8+1), 4 : (w*3, h*8+1), 5 : (w*4, h*8+1),
	6 : (w*0, h*7+1), 7 : (w*1, h*7+1), 8 : (w*2, h*7+1), 9 : (w*3, h*7+1), 10 : (w*4, h*7+1),
	11 : (w*0, h*6+1), 12 : (w*1, h*6+1), 13 : (w*2, h*6+1), 14 : (w*3, h*6+1), 15 : (w*4, h*6+1),
	16 : (w*0, h*5+1), 17 : (w*1, h*5+1), 18 : (w*2, h*5+1), 19 : (w*3, h*5+1), 20 : (w*4, h*5+1),
	21 : (w*0, h*4+1), 22 : (w*1, h*4+1), 23 : (w*2, h*4+1), 24 : (w*3, h*4+1), 25 : (w*4, h*4+1),
	26 : (w*0, h*3+1), 27 : (w*1, h*3+1), 28 : (w*2, h*3+1), 29 : (w*3, h*3+1), 30 : (w*4, h*3+1),
	31 : (w*0, h*2+1), 32 : (w*1, h*2+1), 33 : (w*2, h*2+1), 34 : (w*3, h*2+1), 35 : (w*4, h*2+1),
	36 : (w*0, h*1+1), 37 : (w*1, h*1+1), 38 : (w*2, h*1+1), 39 : (w*3, h*1+1), 40 : (w*4, h*1+1),
	41 : (w*0, h*0+1), 42 : (w*1, h*0+1), 43 : (w*2, h*0+1), 44 : (w*3, h*0+1), 45 : (w*4, h*0+1)
	}

for idx in range(len(quiltImages)):	
	panel = Image.new('RGB', (819, 455))
	
	# Each view on the quilt only has a height of 455, but the three.js scene has a lot of blank space around it, so we can afford to make the pic 480px tall without risking clipping any of the content.
	quiltImages[idx].thumbnail((819, 480), Image.ANTIALIAS)
	
	# We stretch each view by 15% horizontally. Might be wrong, but it just looks better on the Looking Glass. Feel free to experiment with the value.
	quiltImages[idx] = quiltImages[idx].resize((int(quiltImages[idx].width*1.15), quiltImages[idx].height), Image.BICUBIC)
	centered_x_coord = int((819-quiltImages[idx].width)/2)
	centered_y_coord = int((455-quiltImages[idx].height)/2)
	panel.paste(quiltImages[idx], (centered_x_coord, centered_y_coord))
	dst.paste(panel, order[idx+1])
if debug == True:
	dst.show()

print('Step 5/6 - Turning the quilt into a hologram')

##############################################################################
############ Beginning of a code block copyrighted by SURFsara BV ############
############        See LICENSE_SURFsaraBV for full license       ############
class Calibration:
	def __init__(self):
		config = json.loads(config_json)
		self.screenW = int(config['screenW']['value'])
		self.screenH = int(config['screenH']['value'])
		self.DPI = int(config['DPI']['value'])
		self.pitch = config['pitch']['value']
		self.slope = config['slope']['value']
		self.center = config['center']['value']
		self.screenInches = self.screenW / self.DPI
		self.pitch = self.pitch * self.screenInches * cos(atan(1.0/self.slope))
		self.tilt = self.screenH/(self.screenW * self.slope)
		self.subp = 1.0 / (3*self.screenW) * self.pitch

calibration = Calibration()
screenW = calibration.screenW
screenH = calibration.screenH
tilt = calibration.tilt
pitch = calibration.pitch
center = calibration.center
subp = calibration.subp
TILES = (5, 9)
INV_TILES = (1.0/TILES[0], 1.0/TILES[1])

def quilt_map(pos, a):
	tile = [TILES[0] - 1, 0]
	a = a%1 * TILES[1]
	tile[1] += floor(a)
	a = a%1 * TILES[0]
	tile[0] += -floor(a)
	res = [pos[0] + tile[0], pos[1] + tile[1]]
	res[0] /= TILES[0]
	res[1] /= TILES[1]
	return res

def quilt_tile(a):
	tile = [TILES[0] - 1, 0]
	a = a%1 * TILES[1]
	tile[1] += floor(a)
	a = a%1 * TILES[0]
	tile[0] += -floor(a)
	return tile

def pixel_color(qpx, u, v):
	a = (u + (1.0 - v)*tilt)*pitch - center
	tile = quilt_tile(a)
	r_pos = (
	(u + tile[0]) * INV_TILES[0],
	(v + tile[1]) * INV_TILES[1]
	)
	tile = quilt_tile(a + subp)
	g_pos = (
	(u + tile[0]) * INV_TILES[0],
	(v + tile[1]) * INV_TILES[1]
	)
	tile = quilt_tile(a + 2*subp)
	b_pos = (
	(u + tile[0]) * INV_TILES[0],
	(v + tile[1]) * INV_TILES[1]
	)
	r = qpx[r_pos[0]*QWIDTH, r_pos[1]*QHEIGHT][0]
	g = qpx[g_pos[0]*QWIDTH, g_pos[1]*QHEIGHT][1]
	b = qpx[b_pos[0]*QWIDTH, b_pos[1]*QHEIGHT][2]
	return (r, g, b)
	
QWIDTH, QHEIGHT = dst.size
qpx = dst.load()
outimg = Image.new('RGB', (screenW, screenH))
opx = outimg.load()
for j in range(screenH):
	v = j / screenH
	for i in range(screenW):
		u = i / screenW
		opx[i, j] = pixel_color(qpx, u, v)
del qpx
del opx
############ End of the code block copyrighted by SURFsara BV ############
##########################################################################

def add_to_album(image_path, album_name):
	try:
		album = [a for a in photos.get_albums() if a.title == album_name][0]
	except IndexError:
		album = photos.create_album(album_name)
	asset = photos.create_image_asset(image_path)
	album.add_assets([asset])
	os.remove(image_path)

outimg.save(output_filename)
print('Step 6/6 - Saving the hologram to an album')
add_to_album(output_filename, 'Looking Glass')
time.sleep(2)
print('Done.')
