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
	safePosition = file.readUInt()
	file.seek(safePosition, NOESEEK_ABS)
	
	
	#material code starts here
	print("Scanning for material info from " + hex(file.tell()))
	dataFinder = file.readUInt()
	while dataFinder != 17235971: #0x03000701
		dataFinder = file.readUInt()
		
	#material data found; let's read our first texture name.
	#file.seek(4,1) #this goes straight to the texture
	
	#navigate to textureID
	file.seek(-28,1)
	print("First Texture found at " + hex(file.tell()))
	textureID = file.readUInt()
	#check for magic numbers 27 lines
	#(432 bytes + the 4 we just read) above.
	file.seek(-436,1)
	materialStart = file.readUInt()
	matID = file.readUInt()
	#backtrack
	file.seek(428,1)
	#navigate to texture name
	file.seek(28,1)

	complexMaterials = False
	if materialStart == 3 or materialStart == 7:
		complexMaterials = True
	else:
		matID = 0

	finishedMaterials = False
	materialComplete = False
	textureIsNamed = False
	textureJump = 432
	texName = {}
	textures = {}
	materials = {}
	#I could use a dictionary, but it's easier
	#if I just use two arrays for this.
	materialID = {}
	materialAltID = {}

	#set first materialID
	materialID[0] = matID
	materialAltID[0] = matID

	matCount = 0
	texList = []
	#building materials
	while finishedMaterials == False:
		textures = {}
		texCount = 0
		#is the current material an alternate?
		if matCount > 0:
			if materialID[matCount -1] == materialID[matCount]:
				#if so, we be careful about reading textures.
				print("this material is an alternate")
				if file.readUInt() == 0:
					materialComplete = True
				file.seek(-4,1)
		#done checking for alts. now we'll build the material.
		while materialComplete == False:   
			i = 0
			texName = {}
			while textureIsNamed == False:
				#checking if we have an extended name
				if file.tell() % 16 == 0:
					nextID = file.readUInt()
					file.seek(-4,1)
					if textureID == nextID - 2: #if we do, the string is complete.
						textureIsNamed = True
						continue
				texChar = file.readByte()
				if texChar != 0:
					texName[i] = texChar
					#print(texName[i])
				else:
					textureIsNamed = True
				i = i + 1
			#now that we have every character,
			#we can construct the texture name.
			textureIsNamed = False
			textures[texCount] = ""
			for char in texName:
				textures[texCount] = textures[texCount] + chr(texName[char])
			#push forward to next textureID
			positionTest = file.tell() % 16
			if positionTest != 0:
				file.seek(16 - positionTest, 1)

			texCount = texCount + 1
			#repeat or end if there is no textureID.
			nextID = file.readUInt()
			file.seek(12,1)
			altNextID = file.readUInt()
			file.seek(-16,1)
			print(hex(file.tell()) + ": texID = " + str(nextID) + " - " + str(textureID))
			print(str(texCount))
			if materialStart == 7 and texCount > 0 and textureID == nextID - 2 and materialAltID[matCount-1] == 399:
				#I'm using a bad condition for this, but this entire loop
				#needs a rewrite anyway.
				textureID = nextID
				file.seek(28,1)
				print("heavy at " + hex(file.tell()))
			elif materialStart == 7 and texCount > 0 and textureID == nextID - 2:
				textureID = nextID
				file.seek(60,1)
				print("light at " + hex(file.tell()) )
			elif textureID == nextID - 2:
				textureID = nextID
				file.seek(28,1)
			elif textureID == altNextID - 3:
				textureID = altNextID
				file.seek(44,1)
			elif complexMaterials == False:
				materialComplete = True
				finishedMaterials = True
			else:
				materialComplete = True
			
		#end of Material/texture loop
		materialComplete = False
		textureJump = 432
		#print(texName)
		print(textures)
		materials[matCount] = textures
		
		
		for tex in textures:
			#problem: how do I get CanvasWidth, CanvasHeight, etc? I gotta study the example Null left.
			texList.append(NoeTexture(textures[tex], 512, 512, open("E:\\GR2\\" +textures[tex] + ".bmp"), noesis.NOESISTEX_RGBA32))
		
		
		#check for the next magic number.
		positionTest = file.tell() % 16
		if positionTest != 0:
			file.seek(16 - positionTest, 1)

		for x in range(7):#while magic number isn't found
			checkedInt = file.readUInt()
			if checkedInt == 3 or checkedInt == 7:
				#set materialID and materialAltID
				materialStart = checkedInt
				materialID[matCount + 1] = file.readUInt()
				if materialID[matCount] == materialID[matCount + 1]:
					file.seek(20,1)
					materialAltID[matCount + 1] = file.readUInt()
					file.seek(-24,1)
				else:
					materialAltID[matCount + 1] = materialID[matCount + 1]
				file.seek(-4,1)
				#we found another material. let's
				#do some setup and go back to the main loop.
				if materialAltID[matCount + 1] == 1073741824:
					#this is for the "inner" material.
					#It defaults to 432 every iteration. 
					textureJump = 208
					print("altering jump distance")
					#BUT WAIT! There's more! 
					#Somehow, I'll have to predict the actual ID for this value.
					materialID[matCount + 1] = materialID[matCount] + 10
					materialAltID[matCount + 1] = materialID[matCount + 1]
				print("found new material! " + hex(file.tell()))
				file.seek(textureJump - 4,1)
				textureID = file.readUInt()
				file.seek(28,1)
				print("first texture at " + hex(file.tell()))
				break
			elif x == 6:
				#no more materials; mission complete!
				print("all materials COMPLETE!")
				finishedMaterials = True
			else:
				#nothing definitive.
				#let's jump ahead to read the next Int.
				file.seek(12,1)
		matCount = matCount + 1
	#end of All Materials loop
	print("PRINTING MATERIALS")
	matList = []
	for mat in materials:
		#finally creating materials that Noesis can understand!
		#The material name is the name of the first texture.
		if 0 in materials[mat]:
			MaterialName = materials[mat][0]
			material = NoeMaterial(MaterialName, "E:\\GR2\\" +MaterialName + ".bmp")
			matList.append(material)
		else:
			MaterialName = "Material" + str(mat)
			material = NoeMaterial(MaterialName, "")
			matList.append(material)
		#trueMaterials.append([MaterialName,])
		print(materials[mat])
		file.seek(-4, NOESEEK_REL)
	
	file.seek(safePosition, NOESEEK_ABS)
	
	#beginning of mesh code
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
	meshMaterials  = {}
	dictionaryComplete = False

	while dictionaryComplete == False:
		submesh = False
		vertexCount = file.readUInt()
		checkedInt = file.readUInt()
		if checkedInt >= 3 and checkedInt <= 6:
			#starting a new mesh.
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
			#file.seek(16, NOESEEK_REL) #set to 8 if reading materials
			file.seek(8, NOESEEK_REL)
		else: 
			#this is a submesh.
			index = index - 1
			submesh = True
			#we're gonna step back a bit for the material assignment.
			file.seek(-8, NOESEEK_REL) #remove if not processing materials
		
		
		#get materialID from mesh metadata. This is either 1 more or 1 less 
		#than the materialAltID's we collected earlier.
		thisMaterial = file.readUInt()
			
		#remember, there are no shortcuts for submeshes!
		#also, some meshes use an alternate material as the base.
		print("Mesh" + str(index))
		print("at " + hex(file.tell()))
		print("material ID: " + hex(thisMaterial))
		for mat in materialAltID:
			print(hex(materialAltID[mat]))
			if thisMaterial + 1 == materialAltID[mat]:
				meshMaterials["Mesh" + str(index) + "_" + str(faceIndex)] = mat
				break
			elif (thisMaterial - 1 == materialAltID[mat]) or (thisMaterial >= materialID[mat] and thisMaterial <= materialAltID[mat]):
				count = mat
				while count >= 0:
					if materialID[count] == materialAltID[count]:
						break
					count = count - 1
				meshMaterials["Mesh" + str(index) + "_" + str(faceIndex)] = count
				break
			elif mat + 1 < len(materialAltID):
				if thisMaterial >= materialID[mat] and thisMaterial <= materialAltID[mat + 1]:
					#this accounts for the oddball material used for Kat's grav wisps
					print("Using oddball mat")
					meshMaterials["Mesh" + str(index) + "_" + str(faceIndex)] = mat	
			else:
				if ("Mesh" + str(index) + "_" + str(faceIndex) in meshMaterials) == False: 
					print("WARNING: no suitable material found. Setting to 0")
					meshMaterials["Mesh" + str(index) + "_" + str(faceIndex)] = 0
		print("Determined material: " + str(meshMaterials["Mesh" + str(index) + "_" + str(faceIndex)]))
		file.seek(4, NOESEEK_REL)
		
		
		#Getting face data
		modelDictionary["Face" + str(index) + "_" + str(faceIndex)] = file.readUShort()
		if modelDictionary["Face" + str(index) + "_" + str(faceIndex)] == 0:
			#either there's no further face data, or this was an error check.
			#It may not be needed anymore.
			del(modelDictionary["Face" + str(index) + "_" + str(faceIndex)])
			break
		file.seek(14, NOESEEK_REL)
		#this tells me how much face data is repeated. I can use it to 
		#guess where the next set of useful data begins.
		behaviorIndices = file.readUShort() 
		if behaviorIndices != 3 * modelDictionary["Face" + str(index) + "_" + str(faceIndex)]:
			faceBehaviors["Mesh" + str(index) + "_" + str(faceIndex)] = 6
		else:
			faceBehaviors["Mesh" + str(index) + "_" + str(faceIndex)] = 18
		file.seek(6, NOESEEK_REL)
		#print(hex(file.tell()))
		faceIndices = file.readUInt()
		if modelDictionary["Face" + str(index) + "_" + str(faceIndex)] * 3 != faceIndices:
			#there is no further face data. I can stop looking for new meshes.
			#No need to worry about verts. It involves some logic sports here, 
			#but verts already won't be set if there's no face data.
			dictionaryComplete = True
			del(modelDictionary["Face" + str(index) + "_" + str(faceIndex)])
		file.seek(12, NOESEEK_REL)
		if file.readUInt() == faceIndices * 2:
			file.seek(12, NOESEEK_REL)
		else:
			file.seek(-4, NOESEEK_REL)
		#print(hex(file.tell()))
		faceIndex = faceIndex + 1
		index = index + 1

	print("MODEL DICTIONARY")
	print(modelDictionary)
	print("VERTEX TYPES")
	print(modelVertices)
	print("FACE BEHAVIORS")
	print(faceBehaviors)
	print("MATERIALS")
	print(meshMaterials)

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
		
		#msh = NoeMesh([],[], "mesh" + str(meshCounter), "mat" + str(meshCounter))
		msh = NoeMesh([],[], "mesh" + str(meshCounter), "mat")
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
	mdl.setModelMaterials(NoeModelMaterials(texList, matList))
	mdlList.append(mdl)
	
	
	#printing materials for future reference.
	#for mat in materials:
		#print(materials[mat])
	
	return 1