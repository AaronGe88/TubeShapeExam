#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import os
import pyglet
from pyglet.gl import *
import numpy as np

SIZE = 800
ANGLE_INCREMENT = 5


# def main():
	# caption = "Cylinder (pyglet)"
	# width = height = SIZE
	# resizable = True
	# try:
		# config = Config(sample_buffers=1, samples=4, depth_size=16,
				# double_buffer=True)
		# window = TubeWindows(width, height, caption=caption, config=config,
				# resizable=resizable)
	# except pyglet.window.NoSuchConfigException:
		# window = TubeWindows(width, height, caption=caption,
				# resizable=resizable)
	# path = os.path.realpath(os.path.dirname(__file__))
	# #icon16 = pyglet.image.load(os.path.join(path, "cylinder_16x16.png"))
	# #icon32 = pyglet.image.load(os.path.join(path, "cylinder_32x32.png"))
	# #window.set_icon(icon16, icon32)
	# pyglet.app.run()


def vector(*args):
	return (GLfloat * len(args))(*args)


class TubeWindows(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.set_minimum_size(200, 200)
		self.xAngle = 0
		self.yAngle = 0
		self._initialize_gl()
		self._z_axis_list = pyglet.graphics.vertex_list(2,
				("v3i", (0, 0, -1000, 0, 0, 1000)),
				("c3B", (255, 0, 255) * 2)) # one color per vertex
		
	def _initialize_gl(self):
		glClearColor(195/255, 248/255, 248/255, 1)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_POINT_SMOOTH)
		glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
		glEnable(GL_LINE_SMOOTH)
		glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
		glEnable(GL_COLOR_MATERIAL) # 1
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glLightfv(GL_LIGHT0, GL_POSITION, vector(0.5, 0.5, 1, 0))
		glLightfv(GL_LIGHT0, GL_SPECULAR, vector(0.5, 0.5, 1, 1))
		glLightfv(GL_LIGHT0, GL_DIFFUSE, vector(1, 1, 1, 1))
		glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
		glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vector(1, 1, 1, 1))
		glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE) # 2
		# 1 & 2 mean that we can use glColor*() to color materials
	
	def set_cylinders(self, xyz0, xyz1,radiul,row,tolerance):
		self.start0 = xyz0[0,0:3,:].T
		self.end0 = xyz0[1,0:3,:].T
		#print("start", self.start0)
		self.start1 = xyz1[0,0:3,:].T
		self.end1 = xyz1[1,0:3,:].T
		self.radiul = radiul
		self.tolerance = tolerance
		#print(radiul)
		

	def on_draw(self):
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glPushMatrix()
		glTranslatef(0, -20, -500)
		glRotatef(self.xAngle, 1, 0, 0)
		glRotatef(self.yAngle, 0, 1, 0)
		self._draw_axes()
		#if hasattr(self, "start0"):
		self._draw_cylinder()
		glPopMatrix()


	def _draw_axes(self):
		#glBegin(GL_LINES)				 # x-axis (traditional-style)
		#glColor3f(1, 0, 0)
		#glVertex3f(-1000, 0, 0)
		#glVertex3f(1000, 0, 0)
		#glEnd()
		#pyglet.graphics.draw(2, GL_LINES, # y-axis (pyglet-style "live")
		#		("v3i", (0, -1000, 0, 0, 1000, 0)),
		#		("c3B", (0, 0, 255) * 2))
		#self._z_axis_list.draw(GL_LINES)  # z-axis (efficient pyglet-style)
		pass

	def _draw_cylinder(self):
		tol = self.tolerance
		glPushMatrix()
		try:
			glMatrixMode(GL_MODELVIEW)
			#glLoadIdentity()
			for start, end in zip(self.start0, self.end0):
				glPushMatrix()
				orient = start - end
				#print (start,"\n", end)
				#print("orient", orient)
				distance = np.linalg.norm(orient)
				#print("dist",distance)
				norm_orient = orient / distance
				axis = np.cross(np.array([0.,0.,1.]), norm_orient)
				#print("axis",axis)
				norm_axis = (axis / np.linalg.norm(axis)).tolist()
				angle = np.arccos(np.dot(np.array([0.,0.,1.]), norm_orient) )* 180 / np.pi
				glTranslatef(end[0], end[1],end[2])
				glRotatef(angle,norm_axis[0],norm_axis[1], norm_axis[2])
				cylinder = gluNewQuadric()
				gluQuadricNormals(cylinder, GLU_SMOOTH)
				glColor3ub(0, 255, 0)
				gluCylinder(cylinder, self.radiul + tol,\
							self.radiul+ tol, distance, \
							24, 24)
				glPopMatrix()
				
			glMatrixMode(GL_MODELVIEW)
			for start, end in zip(self.start1, self.end1):
				glPushMatrix()
				orient = start - end
				#print (start,"\n", end)
				#print("orient", orient)
				distance = np.linalg.norm(orient)
				#print("dist",distance)
				norm_orient = orient / distance
				axis = np.cross(np.array([0.,0.,1.]), norm_orient)
				#print("axis",axis)
				norm_axis = (axis / np.linalg.norm(axis)).tolist()
				angle = np.arccos(np.dot(np.array([0.,0.,1.]), norm_orient) )* 180 / np.pi
				glTranslatef(end[0], end[1],end[2])
				glRotatef(angle,norm_axis[0],norm_axis[1], norm_axis[2])
				cylinder = gluNewQuadric()
				gluQuadricNormals(cylinder, GLU_SMOOTH)
				glColor3ub(255, 0, 0)
				gluCylinder(cylinder, self.radiul,\
							self.radiul, distance, \
							24, 24)
				glPopMatrix()
		finally:
			gluDeleteQuadric(cylinder)
		glPopMatrix()
		


	def on_resize(self, width, height):
		width = width if width else 1
		height = height if height else 1
		aspectRatio = width / height
		glViewport(0, 0, width, height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(35.0, aspectRatio, 1.0, 1000.0)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

# Escape is predefined to close the window so no on_key_press() needed
	def on_text_motion(self, motion): # Rotate about the x or y axis
		if motion == pyglet.window.key.MOTION_UP:
			self.xAngle -= ANGLE_INCREMENT
			self.xAngle = 360 if  self.xAngle  < 0 else self.xAngle
		elif motion == pyglet.window.key.MOTION_DOWN:
			self.xAngle += ANGLE_INCREMENT
			self.xAngle = 0 if self.xAngle > 360 else self.xAngle
		elif motion == pyglet.window.key.MOTION_LEFT:
			self.yAngle -= ANGLE_INCREMENT
			self.yAngle = 360 if  self.yAngle  < 0. else self.yAngle
		elif motion == pyglet.window.key.MOTION_RIGHT:
			self.yAngle += ANGLE_INCREMENT
			self.yAngle = 0 if self.yAngle > 360. else self.yAngle
