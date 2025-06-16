using Microsoft.AspNetCore.Mvc;
using OpenCvSharp;
using OpenCvSharp.Face;
using System.ComponentModel;

namespace EyeTracker.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class TrackerController : ControllerBase
    {
        //private static CascadeClassifier faceCascade = new CascadeClassifier("C:/Users/miche/OneDrive/Documents/01_Professional_Projects/CounterpilotAwe/app/EyeTracker/EyeTracker/data/haarcascades/haarcascade_frontalface_default.xml");
        private static CascadeClassifier eyeCascade = new CascadeClassifier("C:/Users/miche/OneDrive/Documents/01_Professional_Projects/CounterpilotAwe/app/EyeTracker/EyeTracker/data/haarcascades/haarcascade_eye.xml");

        private readonly ILogger<TrackerController> _logger;
        public TrackerController(ILogger<TrackerController> logger)
        {
            _logger = logger;
        }

        private Mat GetFaceImage(Mat image)
        {
            CascadeClassifier faceCascade = new CascadeClassifier("C:/Users/miche/OneDrive/Documents/01_Professional_Projects/CounterpilotAwe/app/EyeTracker/EyeTracker/data/haarcascades/haarcascade_frontalface_default.xml");
            Rect[] faceROIs = faceCascade.DetectMultiScale(image);
            if (faceROIs == null)
            {
                return image;
            }
            else
            {
                int maxWidth = faceROIs.Max(obj => obj.Width); //TODO if maxWidth doesn't fit some expected ratio of the image?
                Rect faceROI = faceROIs.First(obj => obj.Width == maxWidth);
                return image[faceROI.X, faceROI.Right, faceROI.Y, faceROI.Top];
            }
        }

        private Mat GetEyeImage(Mat image)
        {
            Rect[] eyeROIs = eyeCascade.DetectMultiScale(image);
            if (eyeROIs == null)
                return image;
            else
            {
                int maxWidth = eyeROIs.Max(obj => obj.Width); //TODO if maxWidth doesn't fit some expected ratio of the image?
                Rect eyeROI = eyeROIs.First(obj => obj.Width == maxWidth);
                using Mat eyeImg = image[eyeROI.X, eyeROI.Right, eyeROI.Y, eyeROI.Top];
                return eyeImg;
            }
        }

        [HttpGet]
        public int[] TrackPupil()
        {
            string imageLocation = "C:/Users/miche/OneDrive/Documents/01_Professional_Projects/CounterpilotAwe/app/EyeTracker/EyeTracker/data/images/genericFace.jpg";
            //string imageLocation = "\"data/images/genericFace.jpg\""
            byte[] image = System.IO.File.ReadAllBytes(imageLocation);
            using Mat img = Mat.FromImageData(image, ImreadModes.Grayscale);
            using Mat faceImg = GetFaceImage(img);
            using Mat eyeImg = GetEyeImage(faceImg);
            return new int[] { img.Height, eyeImg.Height };
        }
    }
}
