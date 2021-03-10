import io
import os
import ui
import sys
import time
import Image
import numpy
import photos
import shutil
import socket
import console
import zipfile
import ImageOps
import objc_util
import matplotlib.cm
import urllib.request
from threading import Event, Thread
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
try:
	import diff_match_patch
except:
	for pth in sys.path:
		if pth[-15:] == 'site-packages-3':
			sp3 = pth + '/'
	with urllib.request.urlopen('https://files.pythonhosted.org/packages/c2/5a/9aa3b95a1d108b82fadb1eed4c3773d19069f765bd4c360a930e107138ee/diff_match_patch-20200713-py3-none-any.whl') as f:
		with open(sp3 + 'dmp.zip', 'wb') as ff:
			ff.write(f.read())
	with zipfile.ZipFile(sp3 + 'dmp.zip') as zf:
		zf.extractall(sp3)
	shutil.rmtree(sp3 + 'diff_match_patch-20200713.dist-info', ignore_errors = True)
	os.remove(sp3 + 'dmp.zip')
	import diff_match_patch

if os.path.isfile('holoplay.js'):
	with open('holoplay.js', 'r') as f:
		holoplay_js = f.read()
else:
	with urllib.request.urlopen('https://cdn.jsdelivr.net/npm/holoplay@0.2.3/holoplay.js') as f:
		holoplay_js_vanilla = f.read().decode('utf-8')
	
	with urllib.request.urlopen('https://raw.githubusercontent.com/jankais3r/driverless-HoloPlay.js/main/holoplay.js.patch') as f:
		diff = f.read().decode('utf-8').replace('\r\n', '\n')
	dmp = diff_match_patch.diff_match_patch()
	patches = dmp.patch_fromText(diff)
	holoplay_js, _ = dmp.patch_apply(patches, holoplay_js_vanilla)
	holoplay_js = holoplay_js.replace(
	# Original calibration:
	'{"configVersion":"1.0","serial":"00000","pitch":{"value":49.825218200683597},"slope":{"value":5.2160325050354},"center":{"value":-0.23396748304367066},"viewCone":{"value":40.0},"invView":{"value":1.0},"verticalAngle":{"value":0.0},"DPI":{"value":338.0},"screenW":{"value":2560.0},"screenH":{"value":1600.0},"flipImageX":{"value":0.0},"flipImageY":{"value":0.0},"flipSubp":{"value":0.0}}',
	# Your calibration:
	'{"configVersion":"1.0","serial":"00000","pitch":{"value":47.56401443481445},"slope":{"value":-5.480000019073486},"center":{"value":0.374184787273407},"viewCone":{"value":40.0},"invView":{"value":1.0},"verticalAngle":{"value":0.0},"DPI":{"value":338.0},"screenW":{"value":2560.0},"screenH":{"value":1600.0},"flipImageX":{"value":0.0},"flipImageY":{"value":0.0},"flipSubp":{"value":0.0}}')
	with open('holoplay.js', 'w') as f:
		f.write(holoplay_js)

if os.path.isfile('three.min.js'):
	with open('three.min.js', 'r') as f:
		three_js = f.read()
else:
	with urllib.request.urlopen('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r124/build/three.min.js') as f:
		three_js = f.read().decode('utf-8')
	with open('three.min.js', 'w') as f:
		f.write(three_js)

if os.path.isfile('OrbitControls.js'):
	with open('OrbitControls.js', 'r') as f:
		orbitcontrols_js = f.read()
else:
	with urllib.request.urlopen('https://cdn.jsdelivr.net/gh/mrdoob/three.js@r124/examples/js/controls/OrbitControls.js') as f:
		orbitcontrols_js = f.read().decode('utf-8')
	with open('OrbitControls.js', 'w') as f:
		f.write(orbitcontrols_js)

if os.path.isfile('pydnet.mlmodel'):
	pass
else:
	with urllib.request.urlopen('https://github.com/FilippoAleotti/mobilePydnet/raw/v2/iOS/AppML/Models/Pydnet.mlmodel') as f:
		pydnet = f.read()
	with open('pydnet.mlmodel', 'wb') as f:
		f.write(pydnet)

allow_ML = True

class Handler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith('rgb.png'):
			self.send_response(200)
			self.send_header('Content-type', 'image/png')
			self.end_headers()
			self.wfile.write(rgbData)
			return
		
		if self.path.endswith('depth.png'):
			self.send_response(200)
			self.send_header('Content-type', 'image/png')
			self.end_headers()
			self.wfile.write(depthData)
			return
		
		if self.path.endswith('holoplay.js'):
			self.send_response(200)
			self.send_header('Content-type', 'text/javascript')
			self.end_headers()
			self.wfile.write((holoplay_js).encode())
			return
		
		if self.path.endswith('three.min.js'):
			self.send_response(200)
			self.send_header('Content-type', 'text/javascript')
			self.end_headers()
			self.wfile.write((three_js).encode())
			return
		
		if self.path.endswith('OrbitControls.js'):
			self.send_response(200)
			self.send_header('Content-type', 'text/javascript')
			self.end_headers()
			self.wfile.write((orbitcontrols_js).encode())
			return
		
		if self.path.endswith('cameracontrol.html'):
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(control.replace('xxx', control_startcamera).replace('yyy', control_sphere).encode())
			return

		if self.path == '/':
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(mode.encode())
			return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

class Server():
	server = None
	def start_server(self):
		self.server = ThreadedHTTPServer(('0.0.0.0', 8080), Handler)
		server_thread = Thread(target = self.server.serve_forever)
		server_thread.daemon = False
		server_thread.start()
	
	def stop_server(self):
		self.server.shutdown()
		self.server.server_close()

# This class uses iOS API to fetch a depth map from the provided image data. The beauty of it is that it works regardless if we have a JPG or a HEIC file.
class CImage(object):
	def __init__(self, chosen_pic_data):
		CIImage = objc_util.ObjCClass('CIImage')
		options = {}
		options['kCIImageAuxiliaryDepth'] = objc_util.ns(True)
		options['kCIImageApplyOrientationProperty'] = objc_util.ns(True)
		self.ci_img = CIImage.imageWithData_options_(chosen_pic_data, options)
	
	def to_png(self):
		global depthSource
		ctx = objc_util.ObjCClass('CIContext').context()
		try:
			extent = self.ci_img.extent()
		except:
			if allow_ML:
				raise('The selected portrait photo does not contain a depth map.')
			else:
				print('The selected portrait photo does not contain a depth map.')
				quit()
		m = ctx.outputImageMaximumSize()
		cg_img = ctx.createCGImage_fromRect_(self.ci_img, extent)
		ui_img = objc_util.UIImage.imageWithCGImage_(cg_img)
		png_data = objc_util.uiimage_to_png(objc_util.ObjCInstance(ui_img))
		depthSource = 'Embedded'
		return png_data

class CoreML(object):
	def __init__(self, chosen_pic):
		self.MLModel = objc_util.ObjCClass('MLModel')
		self.VNCoreMLModel = objc_util.ObjCClass('VNCoreMLModel')
		self.VNCoreMLRequest = objc_util.ObjCClass('VNCoreMLRequest')
		self.VNImageRequestHandler = objc_util.ObjCClass('VNImageRequestHandler')
		
		result = self.classify_asset(chosen_pic)
		if result:
			resultString = str(result)
			resultWidth = int(resultString[resultString.find('width=') + 6:resultString.find(' ', resultString.find('width=') + 6)])
			resultHeight = int(resultString[resultString.find('height=') + 7:resultString.find(' ', resultString.find('height=') + 7)])
			CIImage = objc_util.ObjCClass('CIImage')
			pixelBuffer = result.pixelBuffer
			ci_img = CIImage.imageWithCVPixelBuffer_(pixelBuffer())		
			ctx = objc_util.ObjCClass('CIContext').context()
			cg_img = ctx.createCGImage_fromRect_(ci_img, objc_util.CGRect(objc_util.CGPoint(0, 0), objc_util.CGSize(resultWidth, resultHeight)))
			ui_img = objc_util.UIImage.imageWithCGImage_(cg_img)
			self.png_data = objc_util.uiimage_to_png(objc_util.ObjCInstance(ui_img))
			
	def to_png(self):
		global depthSource
		depthSource = 'CoreML'
		return self.png_data
	
	def load_model(self):
		'''Helper method for downloading/caching the mlmodel file'''
		ml_model_url = objc_util.nsurl('pydnet.mlmodel')
		# Compile the model:
		c_model_url = self.MLModel.compileModelAtURL_error_(ml_model_url, None)
		# Load model from the compiled model file:
		ml_model = self.MLModel.modelWithContentsOfURL_error_(c_model_url, None)
		# Create a VNCoreMLModel from the MLModel for use with the Vision framework:
		vn_model = self.VNCoreMLModel.modelForMLModel_error_(ml_model, None)
		return vn_model
	
	def classify_asset(self, chosen_pic):
		'''The main image classification method.'''
		# img_data = objc_util.ns(chosen_pic.get_image_data().getvalue())
		img_data = chosen_pic.getvalue()
		vn_model = self.load_model()
		# Create and perform the recognition request:
		req = self.VNCoreMLRequest.alloc().initWithModel_(vn_model).autorelease()
		handler = self.VNImageRequestHandler.alloc().initWithData_options_(img_data, None).autorelease()
		success = handler.performRequests_error_([req], None)
		if success:
			return req.results()[0]
		else:
			return None

class debugDelegate (object):
	def webview_should_start_load(self, webview, url, nav_type):
		global wk
		val = urllib.parse.unquote(url)[5:]
		if url.startswith('posx'):
			wk.evaluateJavaScript_completionHandler_('camera.position.x = ' + val, None)
			wk.evaluateJavaScript_completionHandler_('camera.lookAt(0, 0, 0)', None)
		if url.startswith('posy'):
			wk.evaluateJavaScript_completionHandler_('camera.position.y = ' + val, None)
			wk.evaluateJavaScript_completionHandler_('camera.lookAt(0, 0, 0)', None)
		if url.startswith('posz'):
			wk.evaluateJavaScript_completionHandler_('camera.position.z = ' + val, None)
			wk.evaluateJavaScript_completionHandler_('camera.lookAt(0, 0, 0)', None)
		return True

pointcloud = '''
<html>
	<head>
		<style>
			body {
				margin: 0;
			}
			canvas {
				width: 100%;
				height: 100%;
				display: block;
			}
		</style>
		<meta charset="utf-8"/>
		<script src="http://localhost:8080/holoplay.js"></script>
		<script src="http://localhost:8080/three.min.js"></script>
	</head>
	<body>
		<canvas></canvas>
		<script>
			"use strict";
			var camera;
			function loadImage(url) {
				return new Promise((resolve, reject) => {
					const img = new Image();
					img.crossOrigin = "anonymous";
					img.onload = (e) => {
						resolve(img);
					};
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
				const x = (u * (imageData.width - 1)) | 0;
				const y = (v * (imageData.height - 1)) | 0;
				if (x < 0 || x >= imageData.width || y < 0 || y >= imageData.height) {
					return [0, 0, 0, 0];
				} else {
					const offset = (y * imageData.width + x) * 4;
					return Array.from(imageData.data.slice(offset, offset + 4)).map((v) => v / 255);
				}
			}

			async function main() {
				const images = await Promise.all([
					loadImage("http://localhost:8080/rgb.png"), // RGB
					loadImage("http://localhost:8080/depth.png"), // Depth
				]);
				const data = images.map(getImageData);

				const canvas = document.querySelector("canvas");
				const renderer = new THREE.WebGLRenderer({ canvas: canvas });

				// Constants you can experiment with: near, far, camera.position.z, depthSpread, skip, size
				const fov = 70;
				const aspect = 2;
				const near = 1;
				const far = 4000;
				camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
				camera.position.z = 450;

				const scene = new THREE.Scene();
				var holoplay = new HoloPlay(scene, camera, renderer);
				const rgbData = data[0];
				const depthData = data[1];

				const skip = 1;
				const across = Math.ceil(rgbData.width / skip);
				const down = Math.ceil(rgbData.height / skip);

				const positions = [];
				const colors = [];
				const color = new THREE.Color();
				const spread = 200;
				const depthSpread = 350;
				const imageAspect = rgbData.width / rgbData.height;
				const size = 1;

				for (let y = 0; y < down; ++y) {
					const v = y / (down - 1);
					for (let x = 0; x < across; ++x) {
						const u = x / (across - 1);
						const rgb = getPixel(rgbData, u, v);
						const depth = 1 - getPixel(depthData, u, v)[0];

						positions.push((u * 2 - 1) * spread * imageAspect, (v * -2 + 1) * spread, depth * depthSpread - 220);
						colors.push(...rgb.slice(0, 3));
					}
				}

				const geometry = new THREE.BufferGeometry();
				geometry.addAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
				geometry.addAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
				geometry.computeBoundingSphere();
				const material = new THREE.PointsMaterial({ size: size, vertexColors: THREE.VertexColors });
				const points = new THREE.Points(geometry, material);
				scene.add(points);

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

				function render() {
					var timer = setInterval(function () {
						if (resizeRendererToDisplaySize(renderer)) {
							const canvas = renderer.domElement;
							camera.aspect = canvas.clientWidth / canvas.clientHeight;
							camera.updateProjectionMatrix();
						}
						//renderer.render(scene, camera);
						holoplay.render();
						var ctxx = renderer.domElement.getContext("webgl");
						var pixels = new Uint8Array(ctxx.drawingBufferWidth * ctxx.drawingBufferHeight * 4);
						ctxx.readPixels(0, 0, ctxx.drawingBufferWidth, ctxx.drawingBufferHeight, ctxx.R, ctxx.UNSIGNED_BYTE, pixels);
						var pixelSum = pixels.reduce(function (a, b) {
							return a + b;
						}, 0);
						if (pixelSum != 0) {
							clearInterval(timer);
						}
					}, 10);
				}
				render();
			}
			main();
		</script>
	</body>
</html>
'''

mesh = '''
<html>
	<head>
		<style>
			html,
			body {
				margin: 0;
			}
			#c {
				width: 100vw;
				height: 100vh;
				display: block;
			}
		</style>
		<meta charset="utf-8"/>
	</head>
	<body>
		<canvas id="c"></canvas>
		<script src="http://localhost:8080/holoplay.js"></script>
		<script src="http://localhost:8080/three.min.js"></script>
		<script>
			var camera;
			function main() {
				const canvas = document.querySelector("#c");
				const renderer = new THREE.WebGLRenderer({ canvas });

				const fov = 70;
				const aspect = 2; // the canvas default
				const near = 1;
				const far = 5000;
				camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
				camera.position.set(0, 0, 220);
				camera.lookAt(0, 0, 0);

				const scene = new THREE.Scene();
				var holoplay = new HoloPlay(scene, camera, renderer);

				const imgLoader = new THREE.ImageLoader();
				imgLoader.load("http://localhost:8080/depth.png", createHeightmap);

				function createHeightmap(image) {
					// extract the data from the image by drawing it to a canvas
					// and calling getImageData
					const ctx = document.createElement("canvas").getContext("2d");
					const { width, height } = image;
					ctx.canvas.width = width;
					ctx.canvas.height = height;
					ctx.drawImage(image, 0, 0);
					const { data } = ctx.getImageData(0, 0, width, height);

					const geometry = new THREE.Geometry();

					const cellsAcross = width - 1;
					const cellsDeep = height - 1;
					for (let z = 0; z < cellsDeep; ++z) {
						for (let x = 0; x < cellsAcross; ++x) {
							// compute row offsets into the height data
							// we multiply by 4 because the data is R,G,B,A but we
							// only care about R
							const base0 = (z * width + x) * 4;
							const base1 = base0 + width * 4;

							// look up the height for the for points
							// around this cell
							const h00 = width * 0.14 + data[base0] * -1.4;
							const h01 = width * 0.14 + data[base0 + 4] * -1.4;
							const h10 = width * 0.14 + data[base1] * -1.4;
							const h11 = width * 0.14 + data[base1 + 4] * -1.4;

							// compute the average height
							const hm = (h00 + h01 + h10 + h11) / 4;

							// the corner positions
							const x0 = x;
							const x1 = x + 1;
							const z0 = z;
							const z1 = z + 1;

							// remember the first index of these 5 vertices
							const ndx = geometry.vertices.length;

							// add the 4 corners for this cell and the midpoint
							geometry.vertices.push(new THREE.Vector3(x0, h00, z0), new THREE.Vector3(x1, h01, z0), new THREE.Vector3(x0, h10, z1), new THREE.Vector3(x1, h11, z1), new THREE.Vector3((x0 + x1) / 2, hm, (z0 + z1) / 2));

							//      2----3
							//      |\  /|
							//      | \/4|
							//      | /\ |
							//      |/  \|
							//      0----1

							// create 4 triangles
							geometry.faces.push(new THREE.Face3(ndx, ndx + 4, ndx + 1), new THREE.Face3(ndx + 1, ndx + 4, ndx + 3), new THREE.Face3(ndx + 3, ndx + 4, ndx + 2), new THREE.Face3(ndx + 2, ndx + 4, ndx + 0));

							// add the texture coordinates for each vertex of each face.
							const u0 = x / cellsAcross;
							const v0 = z / cellsDeep;
							const u1 = (x + 1) / cellsAcross;
							const v1 = (z + 1) / cellsDeep;
							const um = (u0 + u1) / 2;
							const vm = (v0 + v1) / 2;
							geometry.faceVertexUvs[0].push(
								[new THREE.Vector2(u0, v0), new THREE.Vector2(um, vm), new THREE.Vector2(u1, v0)],
								[new THREE.Vector2(u1, v0), new THREE.Vector2(um, vm), new THREE.Vector2(u1, v1)],
								[new THREE.Vector2(u1, v1), new THREE.Vector2(um, vm), new THREE.Vector2(u0, v1)],
								[new THREE.Vector2(u0, v1), new THREE.Vector2(um, vm), new THREE.Vector2(u0, v0)]
							);
						}
					}

					geometry.computeFaceNormals();

					// center the geometry
					geometry.translate(width / -2, 0, height / -2);

					const loader = new THREE.TextureLoader();
					const texture = loader.load("http://localhost:8080/rgb.png");
					texture.flipY = false;
					texture.minFilter = THREE.LinearFilter;
					
					var material = new THREE.MeshBasicMaterial({ map: texture});
					
					var portrait = new THREE.Mesh(geometry, material);
					
					portrait.rotation.x = 90 * THREE.Math.DEG2RAD;
					scene.add(portrait);
				}

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

				function render() {
					var timer = setInterval(function () {
						if (resizeRendererToDisplaySize(renderer)) {
							const canvas = renderer.domElement;
							camera.aspect = canvas.clientWidth / canvas.clientHeight;
							camera.updateProjectionMatrix();
						}
						//renderer.render(scene, camera);
						holoplay.render();
						var ctxx = renderer.domElement.getContext("webgl");
						var pixels = new Uint8Array(ctxx.drawingBufferWidth * ctxx.drawingBufferHeight * 4);
						ctxx.readPixels(0, 0, ctxx.drawingBufferWidth, ctxx.drawingBufferHeight, ctxx.R, ctxx.UNSIGNED_BYTE, pixels);
						var pixelSum = pixels.reduce(function (a, b) {
							return a + b;
						}, 0);
						if (pixelSum != 0) {
							scene.remove(portrait);
							portrait.dispose();
							portrait = undefined;
							material.dispose();
							material = undefined;
							geometry.dispose();
							geometry = undefined;
							scene.dispose();
							scene = undefined;
							clearInterval(timer);
						}
					}, 10);
				}
				render();
			}

			main();
		</script>
	</body>
</html>
'''

wireframe = '''
<html>
	<head>
		<style>
			html,
			body {
				margin: 0;
			}
			#c {
				width: 100vw;
				height: 100vh;
				display: block;
			}
		</style>
		<meta charset="utf-8"/>
	</head>
	<body>
		<canvas id="c"></canvas>
		<script src="http://localhost:8080/holoplay.js"></script>
		<script src="http://localhost:8080/three.min.js"></script>
		<script>
			var camera;
			function main() {
				const canvas = document.querySelector("#c");
				const renderer = new THREE.WebGLRenderer({ canvas });

				const fov = 70;
				const aspect = 2; // the canvas default
				const near = 1;
				const far = 5000;
				camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
				camera.position.set(0, 0, 15);
				camera.lookAt(0, 0, 0);

				const scene = new THREE.Scene();
				var holoplay = new HoloPlay(scene, camera, renderer);

				const imgLoader = new THREE.ImageLoader();
				imgLoader.load("http://localhost:8080/depth.png", createHeightmap);

				function createHeightmap(image) {
					// extract the data from the image by drawing it to a canvas
					// and calling getImageData
					
					const ctx = document.createElement("canvas").getContext("2d");
					var { width, height } = image;
					width = Math.floor(width / 15);
					height = Math.floor(height / 15);
					ctx.imageSmoothingQuality = "high";
					ctx.imageSmoothingEnabled = true;
					ctx.canvas.width = width;
					ctx.canvas.height = height;
					ctx.drawImage(image, 0, 0, width, height);
					
					const { data } = ctx.getImageData(0, 0, width, height);

					const geometry = new THREE.Geometry();

					const cellsAcross = width - 1;
					const cellsDeep = height - 1;
					for (let z = 0; z < cellsDeep; ++z) {
						for (let x = 0; x < cellsAcross; ++x) {
							// compute row offsets into the height data
							// we multiply by 4 because the data is R,G,B,A but we
							// only care about R
							const base0 = (z * width + x) * 4;
							const base1 = base0 + width * 4;

							// look up the height for the for points
							// around this cell
							const h00 = width * 0.2 + data[base0] * -0.1;
							const h01 = width * 0.2 + data[base0 + 4] * -0.1;
							const h10 = width * 0.2 + data[base1] * -0.1;
							const h11 = width * 0.2 + data[base1 + 4] * -0.1;

							// compute the average height
							const hm = (h00 + h01 + h10 + h11) / 4;

							// the corner positions
							const x0 = x;
							const x1 = x + 1;
							const z0 = z;
							const z1 = z + 1;

							// remember the first index of these 5 vertices
							const ndx = geometry.vertices.length;

							// add the 4 corners for this cell and the midpoint
							geometry.vertices.push(new THREE.Vector3(x0, h00, z0), new THREE.Vector3(x1, h01, z0), new THREE.Vector3(x0, h10, z1), new THREE.Vector3(x1, h11, z1), new THREE.Vector3((x0 + x1) / 2, hm, (z0 + z1) / 2));

							//      2----3
							//      |\  /|
							//      | \/4|
							//      | /\ |
							//      |/  \|
							//      0----1

							// create 4 triangles
							geometry.faces.push(new THREE.Face3(ndx, ndx + 4, ndx + 1), new THREE.Face3(ndx + 1, ndx + 4, ndx + 3), new THREE.Face3(ndx + 3, ndx + 4, ndx + 2), new THREE.Face3(ndx + 2, ndx + 4, ndx + 0));

							// add the texture coordinates for each vertex of each face.
							const u0 = x / cellsAcross;
							const v0 = z / cellsDeep;
							const u1 = (x + 1) / cellsAcross;
							const v1 = (z + 1) / cellsDeep;
							const um = (u0 + u1) / 2;
							const vm = (v0 + v1) / 2;
							geometry.faceVertexUvs[0].push(
								[new THREE.Vector2(u0, v0), new THREE.Vector2(um, vm), new THREE.Vector2(u1, v0)],
								[new THREE.Vector2(u1, v0), new THREE.Vector2(um, vm), new THREE.Vector2(u1, v1)],
								[new THREE.Vector2(u1, v1), new THREE.Vector2(um, vm), new THREE.Vector2(u0, v1)],
								[new THREE.Vector2(u0, v1), new THREE.Vector2(um, vm), new THREE.Vector2(u0, v0)]
							);
						}
					}

					geometry.computeFaceNormals();

					// center the geometry
					geometry.translate(width / -2, 0, height / -2);

					const loader = new THREE.TextureLoader();
					const texture = loader.load("http://localhost:8080/rgb.png");
					texture.flipY = false;
					texture.minFilter = THREE.LinearFilter;
					
					var material = new THREE.MeshBasicMaterial({ map: texture, wireframe: true, wireframeLinewidth: 1.5});
					var portrait = new THREE.Mesh(geometry, material);
					
					portrait.rotation.x = 90 * THREE.Math.DEG2RAD;
					scene.add(portrait);
				}

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

				function render() {
					var timer = setInterval(function () {
						if (resizeRendererToDisplaySize(renderer)) {
							const canvas = renderer.domElement;
							camera.aspect = canvas.clientWidth / canvas.clientHeight;
							camera.updateProjectionMatrix();
						}
						holoplay.render();
						var ctxx = renderer.domElement.getContext("webgl");
						var pixels = new Uint8Array(ctxx.drawingBufferWidth * ctxx.drawingBufferHeight * 4);
						ctxx.readPixels(0, 0, ctxx.drawingBufferWidth, ctxx.drawingBufferHeight, ctxx.R, ctxx.UNSIGNED_BYTE, pixels);
						var pixelSum = pixels.reduce(function (a, b) {
							return a + b;
						}, 0);
						if (pixelSum != 0) {
							scene.remove(portrait);
							portrait.dispose();
							portrait = undefined;
							material.dispose();
							material = undefined;
							geometry.dispose();
							geometry = undefined;
							scene.dispose();
							scene = undefined;
							clearInterval(timer);
						}
					}, 10);
				}
				render();
			}

			main();
		</script>
	</body>
</html>
'''

control = '''
<!DOCTYPE html>
<html>
<head>
	<style>
		html,
		body {
			margin: 0;
		}
	</style>
	<meta charset="utf-8" />
</head>
<body>
	<script src="http://localhost:8080/three.min.js"></script>
	<script src="http://localhost:8080/OrbitControls.js"></script>
	<script>
		report = new Object();
		report.posx = function(log) {
			var iframe = document.createElement("IFRAME");
			iframe.setAttribute("src", "posx:" + log);
			document.documentElement.appendChild(iframe);
			iframe.parentNode.removeChild(iframe);
			iframe = null;
		};
		report.posy = function(log) {
			var iframe = document.createElement("IFRAME");
			iframe.setAttribute("src", "posy:" + log);
			document.documentElement.appendChild(iframe);
			iframe.parentNode.removeChild(iframe);
			iframe = null;
		};
		report.posz = function(log) {
			var iframe = document.createElement("IFRAME");
			iframe.setAttribute("src", "posz:" + log);
			document.documentElement.appendChild(iframe);
			iframe.parentNode.removeChild(iframe);
			iframe = null;
		};
		var camera, scene, renderer;

		function init() {
			scene = new THREE.Scene();
			camera = new THREE.PerspectiveCamera(12.5, window.innerWidth / window.innerHeight, 0.1, 1000);
			camera.position.set(xxx);
			renderer = new THREE.WebGLRenderer();
			renderer.setSize(window.innerWidth, window.innerHeight);
			document.body.appendChild(renderer.domElement);
			const controls = new THREE.OrbitControls(camera, renderer.domElement);
			controls.addEventListener("change", report_camera);
			mesh = new THREE.Mesh(new THREE.SphereGeometry(yyy), new THREE.MeshBasicMaterial({
				color: 0xffffff,
				wireframe: true
			}));
			scene.add(mesh);
		}

		window.addEventListener("resize", function() {
			var width = window.innerWidth;
			var height = window.innerHeight;
			renderer.setSize(width, height);
			camera.aspect = width / height;
			camera.updateProjectionMatrix();
		});

		function render() {
			requestAnimationFrame(render);
			renderer.render(scene, camera);
		}

		function report_camera() {
			report.posx(camera.position.x);
			report.posy(camera.position.y);
			report.posz(camera.position.z);
		}

		init();
		render();
	</script>
</body>
</html>
'''

wk = None
mode = mesh
depthSource = None
control_sphere = '14.667, 8, 8'
control_startcamera = '0, 0, 220'

@objc_util.on_main_thread
def main():
	global wk
	UIScreen = objc_util.ObjCClass('UIScreen')
	
	if len(UIScreen.screens()) > 1:
		second_screen = UIScreen.screens()[1]
		second_screen.overscanCompensation = 0
		bounds = second_screen.bounds()
		
		UIWindow = objc_util.ObjCClass('UIWindow')
		second_window = UIWindow.alloc().initWithFrame_(bounds)
		second_window.setScreen(second_screen)
		second_window.makeKeyAndVisible()
		
		wk = objc_util.ObjCClass('WKWebView').alloc().initWithFrame_(objc_util.CGRect((0, 0), (second_screen.bounds().size.width, second_screen.bounds().size.height - 1))).autorelease()
		second_window.addSubview(wk)
		
		request = objc_util.ObjCClass('NSURLRequest').alloc().init()
		nsurl = objc_util.nsurl('http://localhost:8080')
		x = request.initWithURL_(nsurl)
		wk.loadRequest_(x)
	else:
		print('No secondary screen detected. Connect your Looking Glass.')
		v.close()
		s.stop_server()
		quit()

def modeSelect(sender):
	global wk, mode, control_startcamera, control_sphere, cameracontrol
	if modeSelector.selected_index == 0:
		mode = mesh
		control_startcamera = '0, 0, 220'
		control_sphere = '14.667, 8, 8'
	elif modeSelector.selected_index == 1:
		mode = wireframe
		control_startcamera = '0, 0, 15'
		control_sphere = '1, 8, 8'
	elif modeSelector.selected_index == 2:
		mode = pointcloud
		control_startcamera = '0, 0, 450'
		control_sphere = '30, 8, 8'
	
	request = objc_util.ObjCClass('NSURLRequest').alloc().init()
	nsurl = objc_util.nsurl('http://localhost:8080')
	x = request.initWithURL_(nsurl)
	wk.loadRequest_(x)
	cameracontrol.load_url('http://localhost:8080/cameracontrol.html')

def textureSelect(sender):
	global wk, rgbData
	if textureSelector.selected_index == 0:
		rgbData = chosen_pic_photo_image_buffer.getvalue()
	elif textureSelector.selected_index == 1:
		rgbData = chosen_pic_colormap_image_buffer.getvalue()
	
	request = objc_util.ObjCClass('NSURLRequest').alloc().init()
	nsurl = objc_util.nsurl('http://localhost:8080')
	x = request.initWithURL_(nsurl)
	wk.loadRequest_(x)

def close_button(sender):
	global v, wk, s
	wk.loadHTMLString_baseURL_('', None)
	wk = None
	del wk
	v.close()
	s.stop_server()
	console.clear()
	console.hide_output()
	quit()

# This might break on non-English iOS. Too lazy to test.
for album in photos.get_smart_albums():
	if album.title == 'Portrait':
		my_album = album
		break

# Again using iOS API to get the photo's proper filename
try:
	if allow_ML:
		chosen_pic = photos.pick_asset(assets = photos.get_assets(), title = 'Select a photo')
		# chosen_pic = photos.pick_image(show_albums=True, include_metadata=False, original=True, raw_data=False, multi=False)
	else:
		chosen_pic = photos.pick_asset(assets = my_album.assets, title = 'Select a portrait photo')
	filename, file_extension = os.path.splitext(str(objc_util.ObjCInstance(chosen_pic).originalFilename()))
	assert filename != 'None'
	output_filename = 'Holo_' + filename + '.png'
except:
	quit()

try:
	chosen_pic_image = chosen_pic.get_image(original = False)
except:
	print('Image format (' + file_extension[1:] + ') not supported.')
	quit()
chosen_pic_data = chosen_pic.get_image_data(original = False).getvalue()

# Extract a depth map
try:
	chosen_pic_depth = CImage(objc_util.ns(chosen_pic_data)).to_png()
	chosen_pic_depth_stream = io.BytesIO(chosen_pic_depth)
	chosen_pic_depth_image = Image.open(chosen_pic_depth_stream)
	
	# Some Portrait photos have a completely white depth map. Let's treat those as if there was no depth map at all.
	arr = numpy.array(chosen_pic_depth_image).astype(int)
	if numpy.ptp(arr) == 0:
		if allow_ML:
			raise('The selected portrait photo does not contain a depth map.')
		else:
			print('The selected portrait photo does not contain a depth map.')
			quit()
# If the selected photo does not contain a depth map, let's infer it using coreML
except Exception as e:
	# Hardcoded resolution for the Pydnet model
	chosen_pic_resized = chosen_pic.get_image(original = False).resize((640, 384))
	with io.BytesIO() as bts:
		chosen_pic_resized.save(bts, format = 'PNG')
		chosen_pic_depth = CoreML(bts).to_png()
	chosen_pic_depth_stream = io.BytesIO(chosen_pic_depth)
	chosen_pic_depth_image = Image.open(chosen_pic_depth_stream)
	chosen_pic_depth_image = chosen_pic_depth_image.resize((int(chosen_pic.get_ui_image().size[0]), int(chosen_pic.get_ui_image().size[1])), Image.BICUBIC)
	chosen_pic_depth_image = ImageOps.invert(chosen_pic_depth_image)
	# chosen_pic_depth_image.show()
	arr = numpy.array(chosen_pic_depth_image).astype(int)

# This part takes the depth map and normalizes its values to the range of (0, 180). You can experiment with the value, 255 is the ceiling.
chosen_pic_depth_image_array = (120*(arr - numpy.min(arr))/numpy.ptp(arr)).astype(int)
chosen_pic_depth_image = Image.fromarray(numpy.uint8(chosen_pic_depth_image_array))
# chosen_pic_depth_image = chosen_pic_depth_image.convert('P', palette = Image.ADAPTIVE, colors = 2)
# chosen_pic_depth_image.show()

# Making the images smaller for faster processing.
chosen_pic_image.thumbnail((350, 350), Image.ANTIALIAS)
chosen_pic_depth_image.thumbnail((350, 350), Image.ANTIALIAS)

# When the colormap mode is enabled, we use the colormapped depth data as a texture.
chosen_pic_photo_image_buffer = io.BytesIO()
chosen_pic_colormap_image_buffer = io.BytesIO()

arrx = numpy.array(chosen_pic_depth_image.convert('L')).astype(int)
pre_cmap_array = (255*(arrx - numpy.min(arrx))/numpy.ptp(arrx)).astype(int)
cm = matplotlib.cm.get_cmap('jet')
post_cmap_array = numpy.uint8(numpy.rint(cm(pre_cmap_array)*255))[:, :, :3]
cmap_img = Image.fromarray(post_cmap_array)
cmap_img.save(chosen_pic_colormap_image_buffer, format = 'PNG')

chosen_pic_image.save(chosen_pic_photo_image_buffer, format = 'PNG')
rgbData = chosen_pic_photo_image_buffer.getvalue()
chosen_pic_depth_image_buffer = io.BytesIO()
chosen_pic_depth_image.save(chosen_pic_depth_image_buffer, format = 'PNG')
depthData = chosen_pic_depth_image_buffer.getvalue()

s = Server()
s.start_server()

modeSelector = ui.SegmentedControl(alpha = 0, corner_radius = 5)
modeSelector.segments = ('Mesh' , 'Wireframe', 'Point Cloud')
modeSelector.selected_index = 0
modeSelector.action = modeSelect

textureSelector = ui.SegmentedControl(alpha = 0, corner_radius = 5)
textureSelector.segments = ('Photo' , 'Colormap')
textureSelector.selected_index = 0
textureSelector.action = textureSelect

closeButton = ui.Button(title = 'Close', alpha = 0, background_color = 'black', tint_color = 'white', corner_radius = 5)
closeButton.action = close_button
depthSourceLabel = ui.Label(text = 'Depth Source: ' + depthSource, font = ('<system>', 14), alignment = ui.ALIGN_CENTER, alpha = 0, text_color = 'black')

cameracontrol = ui.WebView(apha = 0, corner_radius = 15)
cameracontrol.delegate = debugDelegate()

v = ui.View()
v.present(style = 'fullscreen', hide_title_bar = True)
v.add_subview(textureSelector)
v.add_subview(modeSelector)
v.add_subview(closeButton)
v.add_subview(depthSourceLabel)
v.add_subview(cameracontrol)
textureSelector.frame = (v.width / 2 - 75, v.height / 2 - 288, 150, 32)
textureSelector.alpha = 1
modeSelector.frame = (v.width / 2 - 125, v.height / 2 - 240, 250, 32)
modeSelector.alpha = 1
closeButton.frame = (v.width / 2 - 40, v.height / 2 - 192, 80, 32)
closeButton.alpha = 1
depthSourceLabel.frame = (v.width / 2 - 90, v.height / 2 - 150, 180, 32)
depthSourceLabel.alpha = 1
cameracontrol.frame = (v.width / 2 - 150, v.height / 2 - 100, 300, 300)
cameracontrol.alpha = 1
cameracontrol.load_url('http://localhost:8080/cameracontrol.html')

main()
try:
	# If you are rendering a complex Three.js scene and the hologram doesn't look right, try increasing the sleep timer.
	# This is a hack around a webkit bug. The window needs to be resized once the rendering completes in order to use correct shader values.
	time.sleep(3)
	wk.setFrame_(CGRect((0, 0), (second_screen.bounds().size.width, second_screen.bounds().size.height)))
except:
	pass
