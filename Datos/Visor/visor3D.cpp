/* \author Geoffrey Biggs */


#include <iostream>

#include <thread>


#include <pcl/common/angles.h> // for pcl::deg2rad

#include <pcl/features/normal_3d.h>

#include <pcl/io/pcd_io.h>

#include <pcl/visualization/pcl_visualizer.h>

#include <pcl/console/parse.h>


using namespace std::chrono_literals;




pcl::visualization::PCLVisualizer::Ptr rgbVis (pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr cloud)

{

  // --------------------------------------------

  // -----Open 3D viewer and add point cloud-----

  // --------------------------------------------

  pcl::visualization::PCLVisualizer::Ptr viewer (new pcl::visualization::PCLVisualizer ("3D Viewer"));

  viewer->setBackgroundColor (1, 1, 1);

  pcl::visualization::PointCloudColorHandlerRGBField<pcl::PointXYZRGB> rgb(cloud);

  viewer->addPointCloud<pcl::PointXYZRGB> (cloud, rgb, "sample cloud");

  viewer->setPointCloudRenderingProperties (pcl::visualization::PCL_VISUALIZER_POINT_SIZE, 1, "sample cloud");

  viewer->addCoordinateSystem (1.0);

  viewer->initCameraParameters ();

  return (viewer);

}




// --------------
// -----Main-----
// --------------

int main (int argc, char** argv)
{

  // --------------------------------------
  // -----Parse Command Line Arguments-----
  // --------------------------------------
  if(argc != 2)
  {
    std::cout<<"ERROR: wrong number of parameters."<<std::endl<<"Usage: $./visor3D 3DPoints_file.pcd"<<std::endl;
    return -1;
  }


  std::cout << "3D RGB colour visualisation example\n";


  pcl::PointCloud<pcl::PointXYZRGB>::Ptr point_cloud_ptr (new pcl::PointCloud<pcl::PointXYZRGB>);
  if (pcl::io::loadPCDFile<pcl::PointXYZRGB> (argv[1], *point_cloud_ptr) == -1) //* load the file
  {
    std::cout<<"ERROR: Couldn't read file "<<argv[1]<<std::endl;

    return (-1);
  }

  std::cout << "Loaded "
            << point_cloud_ptr->width * point_cloud_ptr->height
            << " data points from "<< argv[1] << " with the following fields: "
            << std::endl;

 
  pcl::visualization::PCLVisualizer::Ptr viewer;
  viewer = rgbVis(point_cloud_ptr);


  //--------------------
  // -----Main loop-----
  //--------------------

  while (!viewer->wasStopped ())

  {

    viewer->spinOnce (100);

    std::this_thread::sleep_for(100ms);

  }

}