import torch
import numpy as np
import argparse

from networks.FlowNet2 import FlowNet2  # the path is depended on where you create this module
from frame_utils import read_gen  # the path is depended on where you create this module

if __name__ == '__main__':
    # obtain the necessary args for construct the flownet framework
    parser = argparse.ArgumentParser()
    parser.add_argument('--fp16', action='store_true', help='Run model in pseudo-fp16 mode (fp16 storage fp32 math).')
    parser.add_argument("--rgb_max", type=float, default=255.)
    
    args = parser.parse_args()

    # initial a Net
    net = FlowNet2(args).cuda()
    # load the state_dict
    dict = torch.load("/ext/hoya/optical-flow/FlowNet2_checkpoint.pth.tar")
    net.load_state_dict(dict["state_dict"])

    # load the image pair, you can find this operation in dataset.py
    pim1 = read_gen("/ext/BMW_sampling/20240502/3b90b8b6-0454-402d-a1c2-018eadb1aea2/2024-04-26_10-44-20+02-00--7K90070--3b90b8b6-0454-402d-a1c2-018eadb1aea2/LIDAR_TOP_CENTRAL/__RV__front/L_12131012326657746_F_12131012306701862.jpg")
    pim2 = read_gen("/ext/BMW_sampling/20240502/3b90b8b6-0454-402d-a1c2-018eadb1aea2/2024-04-26_10-44-20+02-00--7K90070--3b90b8b6-0454-402d-a1c2-018eadb1aea2/LIDAR_TOP_CENTRAL/__RV__front/L_12131012376807044_F_12131012373544216.jpg")
    images = [pim1, pim2]
    images = np.array(images).transpose(3, 0, 1, 2)
    im = torch.from_numpy(images.astype(np.float32)).unsqueeze(0).cuda()

    # process the image pair to obtian the flow
    result = net(im).squeeze()


    # save flow, I reference the code in scripts/run-flownet.py in flownet2-caffe project
    def writeFlow(name, flow):
        f = open(name, 'wb')
        f.write('PIEH'.encode('utf-8'))
        np.array([flow.shape[1], flow.shape[0]], dtype=np.int32).tofile(f)
        flow = flow.astype(np.float32)
        flow.tofile(f)
        f.flush()
        f.close()


    data = result.data.cpu().numpy().transpose(1, 2, 0)
    writeFlow("/home/hjj/flownet2-master/data/FlyingChairs_examples/0000007-img.flo", data)
