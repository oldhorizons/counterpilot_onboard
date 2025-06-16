namespace EyeTracker
{
    public class Pupil
    {
        public int ID { get; set; } //won't need if we're running locally but will be needed on a server-based solution
        public int Xloc { get; set; }
        public int Yloc { get; set; }
        public int Diameter { get; set; }
        public List<int> XHistory { get; set; } = new List<int>();
        public List<int> YHistory { get; set; } = new List<int>();
        public List<int> DiameterHistory { get; set; } = new List<int>();
    }
}
