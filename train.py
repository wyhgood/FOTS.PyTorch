import argparse
import json
import logging
import os
import pathlib

from data_loader import SynthTextDataLoaderFactory
from data_loader import OCRDataLoaderFactory
from data_loader.dataset import ICDAR
from logger import Logger
from model.loss import *
from model.model import *
from model.metric import *
from trainer import Trainer
from utils.bbox import Toolbox

logging.basicConfig(level=logging.DEBUG, format='')


def main(config, resume):
    train_logger = Logger()

    # Synth800K
    # data_loader = SynthTextDataLoaderFactory(config)
    # train = data_loader.train()
    # val = data_loader.val()

    # ICDAR 2015
    data_root = pathlib.Path(config['data_loader']['data_dir'])
    ICDARDataset2015 = ICDAR(data_root, year = '2015')
    data_loader = OCRDataLoaderFactory(config, ICDARDataset2015)
    train = data_loader.train()
    val = data_loader.val()

    os.environ['CUDA_VISIBLE_DEVICES'] = ','.join([str(i) for i in config['gpus']])
    model = eval(config['arch'])(config['model'])
    model.summary()

    loss = eval(config['loss'])(config['model'])
    metrics = [eval(metric) for metric in config['metrics']]

    trainer = Trainer(model, loss, metrics,
                      resume=resume,
                      config=config,
                      data_loader=train,
                      valid_data_loader=val,
                      train_logger=train_logger,
                      toolbox = Toolbox)

    trainer.train()


if __name__ == '__main__':
    logger = logging.getLogger()

    parser = argparse.ArgumentParser(description='PyTorch Template')
    parser.add_argument('-c', '--config', default=None, type=str,
                        help='config file path (default: None)')
    parser.add_argument('-r', '--resume', default=None, type=str,
                        help='path to latest checkpoint (default: None)')

    args = parser.parse_args()

    config = None
    if args.resume is not None:
        if args.config is not None:
            logger.warning('Warning: --config overridden by --resume')
        config = torch.load(args.resume)['config']
    elif args.config is not None:
        config = json.load(open(args.config))
        path = os.path.join(config['trainer']['save_dir'], config['name'])
        assert not os.path.exists(path), "Path {} already exists!".format(path)
    assert config is not None

    main(config, args.resume)
