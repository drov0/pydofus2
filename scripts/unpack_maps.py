import os
from pathlib import Path
from tqdm import tqdm
import pydofus2.com.ankamagames.dofus.Constants as Constants
from pydofus2.dataAdapter.d2p import PakProtocol2

work_dir = Path(os.path.dirname(__file__))
D2P_MAPS_PATH = Constants.DOFUS_CONTENT_DIR / "maps" / "maps0.d2p"
out_dir = Constants.MAPS_PATH
d2p_reader = PakProtocol2(D2P_MAPS_PATH)
for fp, fs in tqdm(d2p_reader.iterStreams()):
    mapid_mod_10, mapId = fp.split("/")
    file_output_p = out_dir / mapid_mod_10 / mapId
    if not os.path.exists(file_output_p.parent):
        os.makedirs(file_output_p.parent)
    file_output = open(file_output_p, "wb")
    file_output.write(fs)
    file_output.close()
