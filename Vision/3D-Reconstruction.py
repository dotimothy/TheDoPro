# The Do-Pro 3D Scanning Pipeline
# Timothy Do, Daniel Jilani, Zaya Lazar, Harrison Nguyen

import open3d as o3d
import customStereo as cs
import numpy as np
import cv2 as cv

def create_pcd(img, depth, b, f, cx, cy):
        rows, columns = depth.shape

        dy = np.arange(rows).reshape(-1, 1)*np.ones(columns)
        dx = np.arange(columns)*np.ones(rows).reshape(-1, 1)

        x = (dx - cx) * depth / f
        y = (dy - cy) * depth / f

        pcd = np.array([x.flatten(), y.flatten(), depth.flatten()]).transpose()
        pcdRGB = img.reshape(-1, 3)/255
        
        pcd_o3d = o3d.geometry.PointCloud()  
        pcd_o3d.points = o3d.utility.Vector3dVector(pcd)  
        pcd_o3d.colors = o3d.utility.Vector3dVector(pcRGB) 
        
        return pcd_o3d

def createSTL(inputPCPath,outputSTLPath):
	# Load Point-Cloud file using Open3D
	pcd = o3d.io.read_point_cloud(inputPCPath)
	pcd.estimate_normals()

	# Reconstruct surface and convert to mesh
	mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd)
	mesh.compute_vertex_normals()

	# Convert to STL file
	o3d.io.write_triangle_mesh(outputSTLPath, mesh)

if __name__ == '__main__':
	# pcd = o3d.io.read_point_cloud('piano.ply')
	# o3d.visualization.draw_geometries([pcd], point_show_normal=True)
 	#createSTL('piano.ply','piano.stl')