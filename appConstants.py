verbose = True
roi_size = [900, 1500]
ndi_stream_names = ['CHELLE (NVIDIA GeForce RTX 4060 Ti 1)']
osc_ip = "10.0.0.123"
osc_port = 5006
hyperparams = {
    "historyLength": 1000, #number of pupils to track in history
    "deltaD_tolerance": 0.01, #percent pupil diameter change allowable between captures
    "centerDiff_tolerance": 0.3, #percent pupil position cdifference between models
    "confidence_threshold": 0.6,
}