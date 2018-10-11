#Soi soi soi soisoisoi....
#Noesis Gravity Rush 2 gfx Extractor by Roflcopter.

from inc_noesis import *
import noesis
import rapi

#BE	SURE TO HAVE AN ALTERNATE VERSION THAT DOESN'T USE THE REGISTER.
#.gfx is a common file extension, so maybe it'll be annoying to users who
#make a lot of different rips.
def registerNoesisTypes():
	handle = noesis.register("Gravity Rush 2 Models", ".gfx")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadModel(handle, noepyLoadModel)
	#noesis.logPopup() #please comment out when done.
	return 1
	
NOEPY_HEADER = "GFX2"

def noepyCheckType(data):
	file = NoeBitStream(data)
	if len(data) < 4:
		return 0
	if file.readBytes(4).decode("ASCII").rstrip("\0") != "GFX2":
		return 0 
	return 1
	

#loading the models!
def noepyLoadModel(data, mdlList):
	ctx = rapi.rpgCreateContext()
	file = NoeBitStream(data)
	#time to start reading the file.
	fileComplete = False
	meshCounter = 1
	
	vertexType = 32
	
	file.seek(0x18, NOESEEK_ABS)
	vertStart = file.readUInt() #reading a 4-byte integer in LittleEndian format.
	
	print(str(vertStart))
	
	file.seek(0x14, NOESEEK_ABS)
	file.seek(file.readUInt(), NOESEEK_ABS)
	
	print("Scanning for mesh metadata from " + hex(file.tell()))
	dataFinder = file.readUInt()
	while dataFinder != 2661065091 and dataFinder != 2292097411 and dataFinder != 2661196163 and dataFinder != 10396035:
		file.seek(12, NOESEEK_REL)
		dataFinder = file.readUInt()
	
	file.seek(-20, NOESEEK_REL)
	print("first vertex count found at " + hex(file.tell()))

	#We're gonna build a dictionary
	#of all the vertex and face counts.
	index = 1
	faceIndex = 1
	modelDictionary = {}
	modelVertices = {}
	faceBehaviors = {}
	dictionaryComplete = False

	while dictionaryComplete == False:
		submesh = False
		vertexCount = file.readUInt()
		checkedInt = file.readUInt()
		if checkedInt >= 3 and checkedInt <= 6:
			faceIndex = 1
			modelDictionary["Vertex" + str(index)] = vertexCount
			file.seek(8, NOESEEK_REL) #using vertex type identifier
			vertexID = file.read("II")
			if vertexID == (2661065091, 136):
				modelVertices["Mesh" + str(index)] = 32
			elif vertexID == (2292097411, 0):
				modelVertices["Mesh" + str(index)] = 28
			elif vertexID == (2661065091, 34974):
				modelVertices["Mesh" + str(index)] = 36
			elif vertexID == (2661065091, 34696):
				modelVertices["Mesh" + str(index)] = 40
			elif vertexID == (2292097411, 135):
				modelVertices["Mesh" + str(index)] = 36
			elif vertexID == (2661196163, 34974):
				modelVertices["Mesh" + str(index)] = 36
			elif vertexID == (2661065091, 0):
				modelVertices["Mesh" + str(index)] = 24
			elif vertexID == (10396035, 0):
				modelVertices["Mesh" + str(index)] = 20
			else:
				modelVertices["Mesh" + str(index)] = 32
			file.seek(16, NOESEEK_REL)
		else:
			index = index - 1
			submesh = True
		
		modelDictionary["Face" + str(index) + "_" + str(faceIndex)] = file.readUShort()
		if modelDictionary["Face" + str(index) + "_" + str(faceIndex)] == 0:
			del(modelDictionary["Face" + str(index) + "_" + str(faceIndex)])
			break
		file.seek(14, NOESEEK_REL)
		behaviorIndices = file.readUShort()
		if behaviorIndices != 3 * modelDictionary["Face" + str(index) + "_" + str(faceIndex)]:
			faceBehaviors["Mesh" + str(index) + "_" + str(faceIndex)] = 6
		else:
			faceBehaviors["Mesh" + str(index) + "_" + str(faceIndex)] = 18
		file.seek(6, NOESEEK_REL)
		print(hex(file.tell()))
		faceIndices = file.readUInt()
		if modelDictionary["Face" + str(index) + "_" + str(faceIndex)] * 3 != faceIndices:
			dictionaryComplete = True
			del(modelDictionary["Face" + str(index) + "_" + str(faceIndex)])
		file.seek(12, NOESEEK_REL)
		if file.readUInt() == faceIndices * 2:
			file.seek(12, NOESEEK_REL)
		else:
			file.seek(-4, NOESEEK_REL)
		print(hex(file.tell()))
		faceIndex = faceIndex + 1
		index = index + 1

	print(modelDictionary)
	print(modelVertices)
	print(faceBehaviors)

	file.seek(vertStart, NOESEEK_ABS)

	meshes = []
	
	while fileComplete == False:
		print(" ")
		print("Begin Mesh" + str(meshCounter).zfill(2))
		verts = []
		faces = []
		uvs = []
		
		dp = 0x400 #(1024)
		meshComplete = False

		#determining the vertex type
		vertexType = modelVertices["Mesh" + str(meshCounter)]
		#set vertex and uv data simultaneously
		vertCount = 0
		seekUV = (8,24)

		if vertexType <= 28:
			seekUV = (4,20)
		print("vertexType: " + str(vertexType))
		print("Vertices: " + hex(file.tell()))
		
		#vertBuff = file.readBytes(modelDictionary["Vertex" + str(meshCounter)] * vertexType)
		
		print(hex(file.tell()))
		
		while vertCount < modelDictionary["Vertex" + str(meshCounter)]:
			#read vertex
			v1 = file.readFloat()
			v2 = file.readFloat()
			v3 = file.readFloat()
			verts.append(NoeVec3((v1,v2,v3)))
			file.seek(seekUV[0], NOESEEK_REL) #seek to uv data
			u1 = file.readShort()
			u2 = file.readShort()
			u1 /= dp
			u2 /= dp
			uvs.append(NoeVec3((u1,-u2, 0)))
			file.seek(vertexType - seekUV[1], NOESEEK_REL) #seek next vertex
			vertCount = vertCount + 1
		#end vertex & uv data
		
		print(hex(file.tell()) + " Count: " + str(vertCount))
		
		padding = True
		#loop to reach face data
		while padding == True:
			#print(hex(file.tell()))
			checkedByte = file.readUByte()
			if checkedByte != 0:
				file.seek(-1, NOESEEK_REL)
				padding = False
		#end loop
		#now we need to confirm tht we're
		#starting at the right place.
		while file.tell() % 32 != 0:
			file.seek(-1, NOESEEK_REL)
		
		meshComplete = False
		
		print("Faces: " + hex(file.tell()))
		
		#face data    
		faceIndex = 1
		faceCount = 0
		subCount40 = 0
		faceBuff = 0
		
		
		while meshComplete == False:
			faceType6 = False
			if faceBehaviors["Mesh" + str(meshCounter) + "_" + str(faceIndex)] == 6:
				faceType6 = True
			submesh = False
			if faceIndex > 1:
				print("Count: " + str(faceCount + 1) + "- Submesh at "  + hex(file.tell()))
			for i in range( modelDictionary["Face" + str(meshCounter) + "_" + str(faceIndex)]):
				f1 = file.readUShort()
				f2 = file.readUShort()
				f3 = file.readUShort()
				faces.append(f1)
				faces.append(f2)
				faces.append(f3)
				faceCount = i
			#are there submeshes?
			if "Face" + str(meshCounter) + "_" + str(faceIndex + 1) in modelDictionary:
				submesh = True
			else:
				meshComplete = True
			#moving to the next section before
			#we decide to iterate
			if submesh == True:
				if faceType6 == False:
					for i in range(2 *(modelDictionary["Face" + str(meshCounter) + "_" + str(faceIndex)])):
						file.seek(6, NOESEEK_REL)
				elif vertexType == 40:
					if subCount40 == 0:
						subCount40 = subCount40 + 1
					else:
						for i in range(2 *(modelDictionary["Face" + str(meshCounter) + "_" + str(faceIndex)])):
							file.seek(6, NOESEEK_REL)                
				padding = True
				while padding == True:
					checkedByte = file.readUByte()
					if (file.tell()-1) % 32 == 0 and checkedByte == 0:
						print("BRO reading " + hex(file.tell()))
						if file.readUByte() != 0:
							file.seek(-2 , NOESEEK_REL)
							padding = False
							continue
						else:
							file.seek(-1 , NOESEEK_REL)
					elif checkedByte != 0:
						file.seek(-1, NOESEEK_REL)
						padding = False
				faceIndex = faceIndex + 1
				print(hex(file.tell()))
			elif faceType6 == False:
				for i in range(2 *(modelDictionary["Face" + str(meshCounter) + "_" + str(faceIndex)])):
					file.seek(6, NOESEEK_REL)
		#end face data
		print(hex(file.tell()) + " Count: " + str(faceCount + 1))

		padding = True
		#loop to reach vertex data
		if modelDictionary.get("Vertex" + str(meshCounter + 1)) != None:
			while padding == True:
				#print(hex(file.tell()))
				checkedByte = file.readUByte()
				if (file.tell()-1) % 32 == 0 and checkedByte == 0:
					file.seek(3, NOESEEK_REL)
					print("SQUAD reading " + hex(file.tell()))
					if file.readUByte() != 0:
						file.seek(-5 , NOESEEK_REL)
						padding = False
						continue
					else:
						file.seek(-4 , NOESEEK_REL)
				elif checkedByte != 0:
					file.seek(-1, NOESEEK_REL)
					padding = False
		#end loop
				
		#material
		#material = mrp.create_material("Material" + str(meshCounter).zfill(2))
		#material.set_color(random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
		#material.set_texture("C:\\Users\\freez\\Pictures\\GR2\\kit01_face_00.bmp", "RGB", True)
		#end material
		
		msh = NoeMesh([],[], "mesh" + str(meshCounter), "mat" + str(meshCounter))
		msh.setIndices(faces)
		msh.setPositions(verts)
		msh.setUVs(uvs)
		
		#mdlList.append(NoeModel([msh], [], []))
		meshes.append(msh)
		
		print("Mesh" + str(meshCounter).zfill(2) + " complete")
		meshCounter = meshCounter + 1
		#failsafe for infinite loops
		#print(modelDictionary.get("Vertex" + str(meshCounter)))
		if meshCounter == 100 or modelDictionary.get("Vertex" + str(meshCounter)) == None:
			  print("File Complete at Mesh" + str(meshCounter - 1).zfill(2))
			  fileComplete = True
	#mrp.render("All")
	#rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, modelDictionary["Vertex" + str(meshCounter)], noesis.RPGEO_POINTS, 1)

	mdl = NoeModel(meshes)
	mdlList.append(mdl)
	
	return 1