import numpy as np
import scipy.optimize
import scipy.integrate
import tube_window as tw
import pyglet
from pyglet.gl import *

SIZE = 800
def ybc_2_xyz(ybc, r):
	y= ybc[:, 0]
	row = ybc.shape[0]
	
	one_cols = np.ones(row)
	"""初始化起止点"""
	st_pts = np.zeros([row,4])
	st_pts[:, 3] = one_cols
	
	end_pts = np.zeros([row,4])
	end_pts[:, 1] = - y
	end_pts[:, 3] = one_cols


	"""得到变换矩阵0"""
	mat = np.zeros([4,4,row])
	#print(r, ybc.shape)
	trsf = mat_transfer(np.concatenate([ybc,\
										r.T],\
										axis = 1 ))
	#print(trsf[:,:,0])
	#print(trsf_0[:,:,0],"\n",trsf_1[:,:,0])
	for jj in range(row):
		mat[:,:,jj] = np.eye(4)
		for ii in range(row - 1, jj - 1, -1):
			#print(jj,ii)
			mat[:,:,jj] = np.dot(mat[:,:,jj], trsf[:,:,ii])
	#print(mat[1,:,:])
	xyz = trans_2_xyz(mat, st_pts, end_pts)
	return xyz
	
def tube_shape_exam(ybc0, ybc1, r):
	row = ybc1.shape[0]

	xyz0 = ybc_2_xyz(ybc0,r)
	xyz1 = ybc_2_xyz(ybc1,r)
	#print(xyz0[:,:,-1],"\n",xyz1[:,:,-1])
	x0 = [0.,0.,0.,0.,0.,0.]
	res = scipy.optimize.minimize(opt_problem, x0, \
								args = [xyz0,xyz1,row], \
								method='Nelder-Mead')
	#print(res.x)
	
	xyz_mod = np.zeros([2,4,row])
	matr = rotate_move(res.x[0:3],res.x[3:6])	
	for ii in range(row):
		start = xyz1[0,:,ii]
		end = xyz1[1,:,ii]
		start_mod = np.dot(start, matr)
		end_mod = np.dot(end, matr)
		xyz_mod[0,:,ii] = start_mod
		xyz_mod[1,:,ii] = end_mod
	#print(xyz_opt[:,:,0])
	diff = (xyz_mod - xyz0)[:,0:3,:] ** 2
	gap = 0.
	for ii in range(row):
		gap = gap + np.sum(np.sqrt(np.sum(diff[:,:,ii],axis = 1)))
	#print(gap)
	"""Display"""
	caption = "Shape Exam"
	width = height = SIZE
	resizable = True
	try:
		config = Config(sample_buffers=1, samples=4, depth_size=16,
				double_buffer=True)
		window = tw.TubeWindows(width, height, caption=caption, config=config,
				resizable=resizable)
	except pyglet.window.NoSuchConfigException:
		window = tw.TubeWindows(width, height, caption=caption,
				resizable=resizable)
	window.set_cylinders(xyz0, xyz_mod,8,row)
	pyglet.app.run()
	return xyz0, xyz_mod
	
def mat_transfer(ybcr):
	row = ybcr.shape[0]
	y = ybcr[:, 0]
	b = ybcr[:, 1] * np.pi / 180.
	c = ybcr[:, 2] * np.pi / 180.
	r = ybcr[:, 3]
	
	A1 = np.zeros([4,4,row])
	A2 = np.zeros([4,4,row])
	A31 = np.zeros([4,4,row])
	A32 = np.zeros([4,4,row])
	A33 = np.zeros([4,4,row])
	A3t = np.zeros([4,4,row])
	A3 = np.zeros([4,4,row])
	
	for ii in range(row):
		A1[:,:,ii] = np.eye(4)
		A2[:,:,ii] = np.eye(4)
		A31[:,:,ii] = np.eye(4)
		A32[:,:,ii] = np.eye(4)
		A33[:,:,ii] = np.eye(4)
		
	A1[1,3,:] = y
	A2[0,0,:] = np.cos(b)
	A2[0,2,:] = np.sin(b)
	A2[2,0,:] = -np.sin(b)
	A2[2,2,:] = np.cos(b)
	#print(A2[:,:,0])
	A31[0,3,:] = - r
	A32[0,0,:] = np.cos(c)
	A32[0,1,:] = np.sin(c)
	A32[1,0,:] = -np.sin(c)
	A32[1,1,:] = np.cos(c)
	
	A33[0,3,:] = r
	#print("A33",A33[:,:,0])
	for ii in range(row):
		A3t[:,:,ii] = np.dot(A33[:,:,ii], A32[:,:,ii])
	#print("A3t",A3t[:,:,0])
	for ii in range(row):
		A3[:,:,ii] = np.dot(A3t[:,:,ii], A31[:,:,ii])
	#print("A3",A3[:,:,0])
	transfer = np.zeros([4,4,row])
	for ii in range(row):
		transfer[:,:,ii] = np.dot(np.dot(A3[:,:,ii], A2[:,:,ii]), \
							A1[:,:,ii])
	#print("tr",transfer[:,:,0])
	return transfer
	
def trans_2_xyz(transfer, st_pts, end_pts):
	row = st_pts.shape[0]
	seg = np.zeros([2,4,row])
	for ii in range(row):
		#print(mat_transfer[:,:,ii],"\n",st_pts[ii,:])
		seg[0,:,ii] = np.dot(transfer[:,:,ii],\
							st_pts[ii,:].T)
		seg[1,:,ii] = np.dot(transfer[:,:,ii],\
							end_pts[ii,:].T)
	
	return seg

def fit_line(xyz):
	vectors = xyz[0,0:3,:] - xyz[1,0:3,:]
	row = xyz.shape[2]

	line = np.zeros([row + 1, 3])
	line[0,:] = xyz[0,0:3,0]
	for ii in range(row - 1):
		x0 = xyz[0,0,ii]
		y0 = xyz[0,1,ii]
		z0 = xyz[0,2,ii]
		
		x1 = xyz[1,0,ii + 1]
		y1 = xyz[1,1,ii + 1]
		z1 = xyz[1,2,ii + 1]
		
		m0 = vectors[0,ii]
		m1 = vectors[0,ii + 1]
		n0 = vectors[1,ii]
		n1 = vectors[1,ii + 1]
		p0 = vectors[2,ii]
		p1 = vectors[2,ii+1]
		
		A0 = np.linalg.det([[n0, p0],\
							[n1,p1]])
		B0 = np.linalg.det([[p0,m0],\
							[p1,m1]])
		C0 = np.linalg.det([[m0,n0],
							[m1,n1]])
		A1 = np.linalg.det([[n1,B0],\
							[p1,C0]])
		B1 = np.linalg.det([[p1,C0],\
							[m1,A0]])
		C1 = np.linalg.det([[m1,A0],\
							[n1,B0]])
							
		delta0 = np.linalg.det([[A0,B0,C0],\
								[A1,B1,C1],\
								[n0,-m0,0]])
		D0 = A1 * (x1 - x0) + \
			B1 * (y1 - y0) + \
			C1 * (z1 - z0)
		Gx = x0 - D0 * m0 * C0 / delta0
		Gy = y0 - D0 * n0 * C0 / delta0
		Gz = z0 + D0 * (A0 * m0 + B0 * n0) / delta0
			
		A2 = n0 * C0 + \
			p0 * np.linalg.det([[m0,p0],[m1,p1]])
		B2 = p0 * A0 + \
			m0 * np.linalg.det([[n0,m0],[n1,m1]])
		C2 = m0 * B0 + \
			n0 * np.linalg.det([[p0,n0],[p1,n1]])
		
		delta1 = n1 * np.linalg.det([[B0,C0],[B2,C2]]) + \
				m1 * np.linalg.det([[A0,C0],[A2,C2]])
		D1 = A2 * (x0 - x1) + \
			B2 * (y0 - y1) + \
			C2 * (z0 - z1)
		
		Hx = x1 - D1 * m1 * C0 / delta1
		Hy = y1 - D1 * n1 * C0 / delta1
		Hz = z1 + D1 * (A0 * m1 + B0 * n1) / delta1
		
		line[ii + 1,:] = np.array([(Gx + Hx)/2,\
						(Gy + Hy)/2, \
						(Gz + Hz)/2])
	line[row,:] = xyz[1,0:3,row-1]
	return line
		

		
def rotate_move(angles, moves):
	angles = angles * np.pi / 180.
	rx = angles[0]
	ry = angles[1]
	rz = angles[2]
	mx = moves[0]
	my = moves[1]
	mz = moves[2]
	rx_matrix = np.eye(4)
	ry_matrix = np.eye(4)
	rz_matrix = np.eye(4)
	m_matrix = np.eye(4)
	
	rx_matrix[0,0] = np.cos(rx)
	rx_matrix[0,1] = -np.sin(rx)
	rx_matrix[1,0] = np.sin(rx)
	rx_matrix[1,1] = np.cos(rx)

	ry_matrix[0,0] = np.cos(ry)
	ry_matrix[0,2] = -np.sin(ry)
	ry_matrix[2,0] = np.sin(ry)
	ry_matrix[2,2] = np.cos(ry)

	rz_matrix[1,1] = np.cos(rz)
	rz_matrix[1,2] = -np.sin(rz)
	rz_matrix[2,1] = np.sin(rz)
	rz_matrix[2,2] = np.cos(rz)
	

	m_matrix[3,0:3] = np.array([mx,my,mz])
	
	r_m_matrix = np.dot(m_matrix,\
						np.dot(rz_matrix,\
							np.dot(ry_matrix,\
									rx_matrix)))
	#print(r_m_matrix)
	return r_m_matrix

def opt_problem(p,args):
	
	xyz0 = args[0]
	xyz1 = args[1]
	row = args[2]
	angle = p[0:3]
	move = p[3:6]
	matr = rotate_move(angle,move)	

	xyz1_mod = np.zeros([2,4,row])
	for ii in range(row):
		start = xyz1[0,:,ii]
		end = xyz1[1,:,ii]
		start_mod = np.dot(start, matr)
		end_mod = np.dot(end, matr)
		xyz1_mod[0,:,ii] = start_mod
		xyz1_mod[1,:,ii] = end_mod
	#print(xyz_opt[:,:,0])
	diff = (xyz1_mod - xyz0)[:,0:3,:] ** 2
	gap = 0.
	for ii in range(row):
		gap = gap + np.sum(np.sqrt(np.sum(diff[:,:,ii],axis = 1)))
	return gap
	
	
# ybc0 = np.array([[20,10,92],\
				# [20,10,45],\
				# [30,90,92],\
				# [30,90,92],\
				# [50,0,0]])

# ybc1 = np.array([[20,12,90],\
				# [19.5,9.9,46],\
				# [31,90,90],\
				# [31,90,90],\
				# [52,0,0]])
			
# r = np.array([[10,10,10,10,10]])

# tube_shape_exam(ybc0,ybc1,r)
