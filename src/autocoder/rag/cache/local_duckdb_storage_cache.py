import hashlib
import json
import os
import time
import platform
import threading
from multiprocessing import Pool
import functools
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
from loguru import logger
from byzerllm import SimpleByzerLLM, ByzerLLM
from autocoder.utils.llms import get_llm_names

try:
    import duckdb
except ImportError:
    logger.error(
        "DuckDB is not installed, please install it using 'pip install duckdb'"
    )
    raise

from autocoder.common import AutoCoderArgs
from autocoder.common import SourceCode
from autocoder.rag.cache.base_cache import (
    BaseCacheManager,
    DeleteEvent,
    AddOrUpdateEvent,
    FileInfo,
    CacheItem,
)
from autocoder.rag.utils import (
    process_file_in_multi_process,
    process_file_local,
)
from autocoder.rag.variable_holder import VariableHolder
from .failed_files_utils import save_failed_files

if platform.system() != "Windows":
    import fcntl
else:
    fcntl = None


default_ignore_dirs = ["__pycache__", "node_modules", "_images"]


def generate_file_md5(file_path: str) -> str:
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


class DuckDBLocalContext:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self._conn = None

    def _install_load_extension(self, ext_list):
        for ext in ext_list:
            self._conn.install_extension(ext)
            self._conn.load_extension(ext)

    def __enter__(self) -> "duckdb.DuckDBPyConnection":
        if not os.path.exists(os.path.dirname(self.database_path)):
            raise ValueError(
                f"Directory {os.path.dirname(self.database_path)} "
                f"does not exist."
            )

        self._conn = duckdb.connect(self.database_path)
        self._install_load_extension(["json", "fts", "vss"])

        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._conn:
            self._conn.close()


class LocalDuckdbStorage:
    # Pre-computed constant vector for empty content representation
    # Generated with seed=42, variance=0.01, normalized to unit length
    # This avoids runtime random generation and ensures consistent behavior
    EMPTY_CONTENT_VECTOR = [
        0.01586297, -0.00441558, 0.02068446, 0.04863921, -0.00747788, -0.00747736, 0.05043346, 0.02450866, -0.01499305, 0.01732710, -0.01479962, -0.01487346, 0.00772726, -0.06110217, -0.05508666, -0.01795711, -0.03234559, 0.01003575, -0.02899849, -0.04510308,
        0.04680669, -0.00721035, 0.00215657, -0.04550050, -0.01738531, 0.00354240, -0.03675792, 0.01199822, -0.01918189, -0.00931548, -0.01921599, 0.05915402, -0.00043104, -0.03377887, 0.02626865, -0.03898864, 0.00667023, -0.06258367, -0.04241671, 0.00628692,
        0.02358354, 0.00547279, -0.00369332, -0.00961599, -0.04721781, -0.02298881, -0.01471088, 0.03376006, 0.01097373, -0.05630413, 0.01034989, -0.01229792, -0.02161806, 0.01953438, 0.03292581, 0.02974119, -0.02680110, -0.00987495, 0.01057917, 0.03115483,
        -0.01530282, -0.00592917, -0.03533171, -0.03820184, 0.02594868, 0.04331264, -0.00229970, 0.03204865, 0.01154914, -0.02060243, 0.01154146, 0.04911846, -0.00114413, 0.04996818, -0.08366371, 0.02624813, 0.00277992, -0.00954904, 0.00293046, -0.06347464,
        -0.00701540, 0.01140468, 0.04719776, -0.01655138, -0.02581991, -0.01602402, 0.02923412, 0.01049894, -0.01691833, 0.01639162, 0.00310025, 0.03093447, -0.02242064, -0.01046416, -0.01252230, -0.04673855, 0.00945684, 0.00833701, 0.00016330, -0.00749173,
        -0.04520102, -0.01343365, -0.01094487, -0.02562138, -0.00515079, 0.01290370, 0.06023689, 0.00557529, 0.00822508, -0.00237749, -0.06127753, -0.00084674, 0.00192350, 0.07866566, -0.00614321, 0.00963016, -0.00110855, -0.03732269, 0.03649698, 0.02401360,
        0.02526225, -0.02904203, 0.04479939, -0.04476926, 0.01874176, 0.06995400, -0.03163359, -0.01808518, 0.00318245, -0.01607891, -0.04952171, 0.00218961, -0.03392554, 0.01512456, -0.02936257, 0.04949843, -0.02501384, -0.01028530, 0.02598034, -0.03930866,
        0.00726412, 0.04174468, -0.05133629, 0.00589643, 0.00829957, 0.02496815, -0.03950303, -0.04216986, 0.01666863, 0.00948445, 0.00799969, 0.01106411, -0.02171715, 0.00741721, 0.00935951, -0.02281340, 0.05958504, 0.01513224, -0.03804525, 0.02096758,
        -0.03112726, 0.02513619, 0.03700070, -0.02620916, 0.03076621, 0.01318250, 0.02625316, 0.06057564, -0.00783667, -0.02407118, -0.02840737, -0.02605357, -0.00246231, 0.01089497, 0.00883635, 0.02641678, 0.00041523, 0.04641980, -0.00845203, 0.08687083,
        0.01998120, -0.02737403, -0.03419983, 0.01540815, -0.00713647, 0.02280219, 0.01511323, -0.00232585, -0.02704305, -0.04837789, -0.01425982, 0.02734980, 0.00683726, -0.03978369, 0.00553067, 0.01230543, -0.02822671, 0.00490934, 0.00185894, -0.03650169,
        0.01142623, 0.01790911, 0.03458813, 0.03365403, -0.04399700, -0.02995021, 0.01644807, 0.01640818, 0.01644847, 0.12304014, 0.01823186, 0.03626522, 0.03046683, 0.02080271, -0.01006838, 0.02423830, -0.02468081, -0.00756300, -0.01550048, 0.00261472,
        0.07392052, -0.05963264, 0.02191628, -0.05150340, -0.01507153, 0.03477653, 0.00205284, -0.03441866, -0.02284381, 0.02170351, -0.02332486, 0.00691278, 0.00145537, -0.02080939, 0.06846861, 0.02024472, -0.06467459, 0.00595457, -0.02113469, 0.02722316,
        -0.02530980, -0.00366420, 0.01612718, 0.02764860, -0.03833245, -0.01068257, -0.01516777, -0.02086460, 0.05638123, 0.01293342, -0.04026736, 0.02931267, 0.06777280, 0.03297262, -0.04852233, -0.01546441, 0.04045985, -0.02260000, 0.01417374, 0.02473857,
        -0.02960228, -0.00190099, -0.10351253, -0.03271466, -0.00806597, -0.03984898, 0.05213239, -0.04567274, -0.01405318, 0.00417531, 0.04602824, -0.04585543, 0.03714659, 0.00032680, -0.03134528, 0.01475765, 0.00635713, -0.01916842, 0.00222919, -0.01230531,
        0.00362527, 0.02114569, 0.05065075, -0.03953065, 0.06812017, -0.06234152, -0.00484738, 0.01878839, 0.00897371, -0.01988642, -0.00664655, -0.01574439, -0.01882185, 0.02713274, 0.01140158, -0.02212864, 0.02872946, 0.00981386, 0.02595942, 0.02010771,
        -0.02647464, -0.01788984, 0.02386543, 0.01949267, -0.00066751, 0.00374695, 0.04080328, -0.01889232, 0.01747200, -0.00645719, -0.00695183, 0.03509034, 0.02636035, 0.02598010, 0.04169154, 0.00067077, 0.02177873, -0.00990862, 0.01035252, -0.00415623,
        0.00309765, 0.01900683, -0.02613055, 0.06682210, -0.03212799, -0.03877611, 0.03698522, 0.02528240, 0.01993178, 0.02006673, -0.00039111, -0.02865455, 0.00242088, -0.02162571, 0.03114125, -0.00469640, -0.02636293, -0.01026372, 0.01318730, -0.01800301,
        -0.02625828, 0.00778235, 0.00782321, -0.01618965, -0.01504299, 0.00741070, -0.04624576, -0.04494851, -0.02294411, -0.00681661, 0.00992909, 0.04711671, 0.02739006, -0.00510777, -0.00060730, -0.03201660, -0.00059123, -0.00921855, 0.01030628, -0.02641830,
        0.01658576, 0.04894927, -0.00347334, 0.01282899, 0.02204031, -0.01281330, 0.00715658, 0.00040215, 0.00311937, -0.02468670, 0.00078275, 0.01590398, 0.04634346, 0.03063510, 0.06876365, -0.02450587, 0.02785827, 0.00585518, 0.06993315, -0.02581367,
        -0.02681721, -0.01914210, -0.06782835, -0.01679042, -0.02424352, 0.00480295, 0.01091426, 0.05991705, 0.03035256, -0.01842389, -0.02869161, 0.01570984, -0.04216273, 0.05848914, 0.03766639, -0.01498351, -0.05471036, 0.04323702, -0.00365792, 0.03953068,
        -0.05091935, -0.01914153, 0.00016746, 0.00150036, -0.01437321, 0.01989122, -0.03409533, -0.00454701, 0.00384174, 0.01642903, 0.02272600, -0.03591637, -0.04899319, 0.04080366, 0.01061272, -0.02390353, 0.04953731, 0.00369416, 0.03766182, 0.00215626,
        0.06581167, 0.05605825, -0.00795087, 0.03102791, 0.02061061, 0.04370837, -0.03081562, 0.02190962, 0.03380165, -0.05616679, -0.03778833, -0.06512455, -0.00860373, 0.02291530, 0.04797900, 0.00236628, 0.05201117, -0.04407467, -0.05439891, -0.00177396,
        0.01226544, -0.00104413, -0.06602546, -0.00284612, -0.04165930, 0.02138654, 0.01170762, -0.03001583, -0.01641076, -0.03382685, -0.00200171, 0.03050325, -0.03147997, 0.01609714, -0.01693421, -0.02532104, -0.00341810, -0.03306131, -0.01768124, -0.03825521,
        0.06274511, 0.00112617, -0.02234631, 0.00683362, -0.00358729, -0.00705685, 0.01961392, 0.02419163, -0.01694199, -0.01838923, -0.00878400, -0.07351374, -0.04838887, 0.04365225, 0.05253339, -0.00795317, 0.01841282, 0.00994003, 0.09832658, 0.03575454,
        -0.00408515, -0.03051597, -0.05130318, 0.00649778, -0.02415468, -0.04542084, -0.02064884, -0.03454012, 0.05388025, 0.02815589, -0.00025461, 0.04726323, 0.00247082, -0.02750582, 0.04864222, 0.01721053, -0.03312531, -0.00607862, -0.02796359, -0.04416084,
        0.02957824, 0.06097879, -0.04466440, 0.01797888, -0.02077880, -0.01555675, -0.01891859, -0.02759225, 0.00154958, -0.02653707, 0.00863726, -0.00160440, -0.00763100, -0.02898379, -0.01841967, 0.02412404, 0.01599720, -0.03121903, 0.00317226, 0.02399616,
        -0.05331383, 0.01735265, -0.02116143, 0.01822254, -0.02437531, -0.05764039, -0.05197690, 0.00153563, 0.00829445, -0.02888009, 0.02039397, -0.05306201, -0.00211031, -0.03867479, -0.02081692, 0.00151372, -0.02747801, -0.01228110, 0.03213679, -0.01842351,
        0.02668851, -0.03607811, 0.01691973, 0.04603768, -0.07893399, -0.02544950, 0.01842927, -0.00648442, 0.01185285, -0.01928876, 0.00276532, -0.00497168, 0.03729408, 0.00812514, 0.01078162, -0.01315363, -0.01557210, -0.01381410, 0.01259715, -0.01344448,
        0.00925420, 0.06627963, 0.02782008, -0.01041183, 0.03836175, -0.01303222, -0.06508918, -0.03219406, -0.05974527, -0.01122587, 0.00058821, 0.05353840, 0.01044069, -0.00699715, 0.02648775, -0.07061442, 0.00752454, 0.02461821, -0.04721986, 0.03652672,
        0.01081016, -0.01326256, 0.02020841, 0.07251644, 0.00580805, 0.00792713, -0.01467007, -0.02714048, 0.02651745, -0.02733974, 0.00228553, -0.01525438, 0.01529661, 0.01065577, 0.03313469, -0.01628779, -0.00861868, -0.03125762, -0.01418887, 0.01204940,
        0.02417505, -0.02945011, 0.02777158, 0.04329341, 0.01320338, 0.05993701, -0.02471159, -0.03974907, -0.05680489, 0.04777740, 0.02089770, -0.00177514, 0.00894103, -0.03594342, 0.07810709, 0.00412678, 0.00349361, 0.02317795, 0.01536142, 0.00714992,
        -0.02524445, 0.01505673, 0.06010399, 0.04296709, 0.05087972, -0.01632609, -0.03160384, -0.00401711, 0.00177962, 0.03494390, -0.05405025, 0.04884744, -0.00504611, -0.01363280, -0.03232238, -0.05284920, 0.02628863, 0.00234147, -0.04119596, -0.04135940,
        -0.01072356, 0.05330157, -0.00829026, -0.04800410, -0.00784801, -0.00870965, -0.08612729, -0.00173395, -0.00737508, 0.02223392, 0.05904793, 0.03597778, -0.00858718, -0.03533781, 0.08218235, 0.00189119, 0.00044484, -0.00077045, 0.00632600, -0.00461027,
        -0.01832037, -0.01746439, -0.00104600, -0.01735472, -0.02276531, 0.00339894, -0.00814291, 0.04803125, -0.08466089, 0.03485817, 0.03979475, -0.06621542, -0.01094401, -0.01186227, -0.04495004, -0.02484021, -0.03546715, 0.05596019, 0.02988166, 0.04060815,
        0.02304719, -0.03605719, -0.01675098, 0.01562858, -0.03902965, 0.02277019, -0.00767499, -0.01197021, 0.02270509, 0.01418791, -0.01152775, 0.03702415, -0.03452464, 0.01967041, 0.01894117, -0.00988562, 0.01041533, -0.03995534, 0.02950956, -0.00590500,
        -0.01669359, 0.03350097, -0.02249379, -0.04498037, -0.04971223, 0.01935342, -0.04089156, 0.05604079, -0.06648812, 0.05417772, 0.00673902, -0.00308861, -0.01740244, 0.01274674, -0.00120190, 0.03523485, 0.00364795, 0.00480001, -0.01161225, -0.00181861,
        0.00982990, -0.05461563, -0.04305541, 0.02373675, 0.00545673, -0.00587566, 0.00058870, 0.01110031, -0.01723767, -0.02485580, 0.00625448, -0.03124514, 0.01303789, -0.05437340, 0.03286693, 0.01509279, 0.00817652, 0.03138304, 0.05318829, 0.03239474,
        -0.05878983, -0.04086434, -0.01995409, 0.00083324, 0.01653187, -0.02317722, 0.00596455, -0.02412377, -0.01952932, -0.04492288, -0.02948421, -0.04316716, -0.03116531, 0.03364891, -0.03031983, 0.08406728, 0.01575451, 0.00590289, -0.02741236, 0.02236497,
        -0.01838347, 0.00389648, 0.08175840, -0.00306775, 0.03670299, -0.02245652, -0.00111739, 0.05655197, -0.02002271, 0.05788203, 0.02260264, -0.01796284, 0.02019646, 0.03105932, 0.01985801, -0.05014641, -0.02322172, -0.00790471, -0.00237709, 0.01982167,
        0.00567503, -0.04264532, 0.01214193, 0.01949956, 0.01787737, 0.03451562, 0.02663199, 0.01466429, -0.00224080, -0.05304415, 0.01372021, 0.00663268, 0.00867309, -0.04077401, -0.03452443, 0.03363330, -0.00126323, 0.02176428, 0.00090437, 0.00095029,
        0.02996486, -0.01648031, 0.00306970, -0.01476314, -0.01387599, -0.00987367, 0.00709402, -0.01528923, 0.04010360, -0.02857002, -0.00596790, -0.01404317, 0.04621042, 0.00627714, 0.03295280, -0.04744259, 0.00852847, 0.02841109, 0.00262781, 0.03402699,
        -0.01652003, 0.04500867, 0.07341720, -0.01158755, -0.01422749, 0.04641502, 0.05044493, -0.01669796, -0.01341901, -0.00899902, -0.04293613, -0.02933790, -0.03206806, -0.02452024, -0.00110769, 0.00747984, 0.04951650, -0.03188325, 0.03143514, -0.00683391,
        -0.00157966, 0.02155091, -0.03585505, 0.01221257, 0.00531579, 0.01572683, 0.00923484, 0.07841202, -0.02036675, -0.01695782, -0.01990050, -0.01773962, -0.02035548, 0.03797222, 0.04536497, -0.01822725, -0.02658196, 0.01505504, -0.01763570, 0.02021320,
        0.00648051, -0.04840653, 0.04942085, 0.05735283, -0.01956991, -0.01238157, 0.00912935, 0.01068115, 0.02103115, 0.06419753, -0.00565095, -0.02549428, -0.04404969, -0.02334285, -0.00105794, 0.05731068, -0.01653034, 0.00714685, -0.00052448, 0.03795231,
        0.08069966, -0.01695373, -0.01563065, 0.03334613, 0.02177676, 0.05897611, 0.01864823, -0.01147429, 0.01886305, 0.03540736, 0.02620277, 0.01620021, 0.03406513, 0.03734241, 0.04414038, 0.02071708, -0.00533705, 0.00468542, 0.03853085, -0.02608951,
        0.01177388, -0.01256160, 0.00091799, 0.04082841, 0.00610291, 0.00148299, -0.04342812, 0.02383222, 0.02061407, 0.06908531, -0.00982915, 0.00699875, 0.00796427, 0.05037726, -0.00304334, 0.00891078, 0.01941367, 0.00595952, -0.01425722, 0.00619842,
        0.03428731, -0.03278261, 0.00424650, -0.02235893, 0.03816479, -0.04864422, -0.01784963, 0.01204657, 0.04999629, -0.00209979, -0.01773075, 0.06007629, -0.04624351, -0.07022067, 0.01405222, -0.01603351, -0.03261391, 0.02262194, 0.00778598, -0.01801431,
        -0.04088757, 0.02786264, 0.02076471, -0.00316726, 0.05897387, -0.03417403, -0.04871890, -0.02209665, -0.00145583, 0.00777124, -0.00770407, 0.01124318, -0.03996894, 0.04610781, -0.00262357, 0.03568176, 0.01094521, 0.01458679, 0.01819599, 0.01429794,
        0.02052588, 0.04244758, 0.00627606, 0.02264262, -0.00286578, 0.04599132, -0.02160114, 0.05751451, -0.00128248, -0.04569298, 0.00409112, -0.02174994, 0.02684664, -0.02084208, -0.01424923, -0.06034403, -0.01444477, -0.07740857, -0.05058323, 0.02428447,
        0.02509517, 0.01358734, -0.03088118, -0.00152370, -0.00011505, -0.03699333, 0.04801226, 0.02801928, -0.00705667, 0.00085862, 0.00665488, -0.06520448, -0.00789381, -0.02177973, -0.03198756, -0.00897717, 0.05741059, 0.02046584, -0.01824107, 0.01828590,
        0.04468956, 0.02952893, 0.00190434, -0.02066046, 0.02229833, 0.01256628, 0.02858873, 0.02028473, 0.03351833, -0.01709318, 0.04207206, 0.00631051, 0.06627516, -0.02200978, 0.05543943, 0.00632044, -0.02080357, -0.01545329, -0.01023055, 0.01354609,
        0.01669718, -0.01832158, -0.00077778, 0.06841516
    ]
    EMPTY_CONTENT_TEXT = "empty"

    def __init__(
        self,
        llm: Union[ByzerLLM, SimpleByzerLLM] = None,
        database_name: str = ":memory:",
        table_name: str = "documents",
        embed_dim: Optional[int] = None,
        persist_dir: str = "./storage",
        args: Optional[AutoCoderArgs] = None,
    ) -> None:
        self.llm = llm
        self.database_name = database_name
        self.table_name = table_name
        self.embed_dim = embed_dim
        self.persist_dir = persist_dir
        self.cache_dir = os.path.join(self.persist_dir, ".cache")
        self.args = args
        logger.info("正在启动 DuckDBVectorStore.")

        if self.database_name != ":memory:":
            self.database_path = os.path.join(
                self.cache_dir, self.database_name
            )

        if self.database_name == ":memory:":
            self._conn = duckdb.connect(self.database_name)
            self._install_load_extension(["json", "fts", "vss"])
            self._initialize()
        else:
            if not os.path.exists(self.database_path):
                if not os.path.exists(self.cache_dir):
                    os.makedirs(self.cache_dir)
                self._initialize()
            self._conn = None
        logger.info(
            f"DuckDBVectorStore 初始化完成, 存储目录: {self.cache_dir}, "
            f"数据库名称: {self.database_name}, "
            f"数据表名称: {self.table_name}"
        )

    @classmethod
    def class_name(cls) -> str:
        return "DuckDBVectorStore"

    @property
    def client(self) -> Any:
        """Return client."""
        return self._conn

    def _install_load_extension(self, ext_list):
        for ext in ext_list:
            print(f"Installing extension: {ext}")
            self._conn.install_extension(ext)
            self._conn.load_extension(ext)

    @staticmethod
    def _apply_pca(embedding, target_dim):
        # 生成固定随机投影矩阵（避免每次调用重新生成）
        np.random.seed(42)  # 固定随机种子保证一致性
        source_dim = len(embedding)
        projection_matrix = np.random.randn(source_dim, target_dim) / np.sqrt(
            source_dim
        )

        # 执行投影
        reduced = np.dot(embedding, projection_matrix)
        return reduced

    def _embedding(
        self, context: str, norm: bool = True, dim: int | None = None
    ) -> List[float]:
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                embedding = self.llm.emb_query(context)[0].output
                # check embedding is  valid embedding
                if not isinstance(embedding, list) or not embedding:
                    print(f"Embedding is not valid: {embedding}")
                    raise ValueError(f"Embedding is not valid: {embedding}")

                if dim:
                    embedding = self._apply_pca(
                        embedding, target_dim=dim
                    )  # 降维后形状 (1024,)

                if norm:
                    embedding = embedding / np.linalg.norm(embedding)

                return embedding.tolist()
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(
                        f"Failed to get embedding after {max_retries} "
                        f"attempts: {str(e)}"
                    )
                    raise

                # Sleep between 1-5 seconds before retrying
                sleep_time = 1 + (retry_count * 1.5)
                logger.warning(
                    f"Embedding API call failed (attempt {retry_count}/"
                    f"{max_retries}). Error: {str(e)}. Retrying in "
                    f"{sleep_time:.1f} seconds..."
                )
                time.sleep(sleep_time)

    def _initialize(self) -> None:
        if self.embed_dim is None:
            _query = f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    _id VARCHAR,
                    file_path VARCHAR,
                    content TEXT,
                    raw_content TEXT,
                    vector FLOAT[],
                    mtime FLOAT
                );
            """
        else:
            _query = f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    _id VARCHAR,
                    file_path VARCHAR,
                    content TEXT,
                    raw_content TEXT,
                    vector FLOAT[],
                    mtime FLOAT
                );
            """

        if self.database_name == ":memory:":
            self._conn.execute(_query)
        elif self.database_path is not None:
            with DuckDBLocalContext(self.database_path) as _conn:
                _conn.execute(_query)

    def truncate_table(self):
        _truncate_query = f"""TRUNCATE TABLE {self.table_name};"""
        if self.database_name == ":memory:":
            self._conn.execute(_truncate_query)
        elif self.database_path is not None:
            with DuckDBLocalContext(self.database_path) as _conn:
                _conn.execute(_truncate_query)

    def query_by_path(self, file_path: str):
        _exists_query = f"""SELECT _id FROM {self.table_name} WHERE file_path = ?"""
        query_params = [file_path]
        _final_results = []
        if self.database_name == ":memory:":
            _final_results = self._conn.execute(_exists_query, query_params).fetchall()
        elif self.database_path is not None:
            with DuckDBLocalContext(self.database_path) as _conn:
                _final_results = _conn.execute(_exists_query, query_params).fetchall()
        return _final_results

    def delete_by_ids(self, _ids: List[str]):
        _delete_query = f"""DELETE FROM {self.table_name} WHERE _id IN (?);"""
        query_params = [",".join(_ids)]
        if self.database_name == ":memory:":
            _final_results = self._conn.execute(_delete_query, query_params).fetchall()
        elif self.database_path is not None:
            with DuckDBLocalContext(self.database_path) as _conn:
                _final_results = _conn.execute(_delete_query, query_params).fetchall()
        return _final_results

    def _get_empty_content_vector(self, dim: int | None = None) -> List[float]:
        """
        Get the pre-computed constant vector for empty content.
        This avoids repeated embedding API calls for the fixed "empty" text.
        
        The vector is pre-computed with:
        - Seed: 42 (for reproducibility) 
        - Variance: 0.01 (small values around zero)
        - Normalized to unit length
        
        Args:
            dim: Target dimension for PCA reduction if needed
            
        Returns:
            List of float values representing the empty content vector
        """
        # Apply PCA if dimension reduction is needed
        if dim and len(self.EMPTY_CONTENT_VECTOR) != dim:
            empty_vector_array = np.array(self.EMPTY_CONTENT_VECTOR)
            reduced_vector = self._apply_pca(empty_vector_array, target_dim=dim)
            # Re-normalize after PCA
            reduced_vector = reduced_vector / np.linalg.norm(reduced_vector)
            return reduced_vector.tolist()
        
        return self.EMPTY_CONTENT_VECTOR

    def _node_to_table_row(
        self, context_chunk: Dict[str, str | float], dim: int | None = None
    ) -> Any:
        
        if not context_chunk["raw_content"]:
            context_chunk["raw_content"] = self.EMPTY_CONTENT_TEXT
            print(f"raw_content is empty")        
        context_chunk["raw_content"] = context_chunk["raw_content"][
            : self.args.rag_emb_text_size
        ]
        
        # Use pre-computed constant vector for empty content to avoid repeated embedding API calls
        if context_chunk["raw_content"] == self.EMPTY_CONTENT_TEXT:
            embedding_vector = self._get_empty_content_vector(dim=dim)
        else:
            embedding_vector = self._embedding(context_chunk["raw_content"], norm=True, dim=dim)
            
        return (
            context_chunk["_id"],
            context_chunk["file_path"],
            context_chunk["content"],
            context_chunk["raw_content"],
            embedding_vector,
            context_chunk["mtime"],
        )

    def add_doc(self, context_chunk: Dict[str, str | float], dim: int | None = None):
        """
        {
            "_id": f"{doc.module_name}_{chunk_idx}",
            "file_path": file_info.file_path,
            "content": chunk,
            "raw_content": chunk,
            "vector": chunk,
            "mtime": file_info.modify_time,
        }
        """
        if self.database_name == ":memory:":
            _table = self._conn.table(self.table_name)
            _row = self._node_to_table_row(context_chunk, dim=dim)
            _table.insert(_row)
        elif self.database_path is not None:
            with DuckDBLocalContext(self.database_path) as _conn:
                _table = _conn.table(self.table_name)
                _row = self._node_to_table_row(context_chunk, dim=dim)
                _table.insert(_row)

    def vector_search(
        self,
        query: str,
        similarity_value: float = 0.7,
        similarity_top_k: int = 10,
        query_dim: int | None = None,
    ):
        """
        list_cosine_similarity: 计算两个列表之间的余弦相似度
        list_cosine_distance: 计算两个列表之间的余弦距离
        list_dot_product: 计算两个大小相同的数字列表的点积
        """
        _db_query = f"""
            SELECT _id, file_path, mtime, score
            FROM (
                SELECT *, list_cosine_similarity(vector, ?) AS score
                FROM {self.table_name}
            ) sq
            WHERE score IS NOT NULL
            AND score >= ?
            ORDER BY score DESC LIMIT ?;
        """
        query_params = [
            self._embedding(query, norm=True, dim=query_dim),
            similarity_value,
            similarity_top_k,
        ]

        _final_results = []
        if self.database_name == ":memory:":
            _final_results = self._conn.execute(_db_query, query_params).fetchall()
        elif self.database_path is not None:
            with DuckDBLocalContext(self.database_path) as _conn:
                _final_results = _conn.execute(_db_query, query_params).fetchall()
        return _final_results


efault_ignore_dirs = ["__pycache__", "node_modules", "_images"]


class LocalDuckDBStorageCache(BaseCacheManager):
    def __init__(
        self,
        path,
        ignore_spec,
        required_exts,
        extra_params: Optional[AutoCoderArgs] = None,
        emb_llm: Union[ByzerLLM, SimpleByzerLLM] = None,
        args: Optional[AutoCoderArgs] = None,
        llm: Optional[Union[ByzerLLM, SimpleByzerLLM, str]] = None,
    ):
        self.path = path
        self.ignore_spec = ignore_spec
        self.required_exts = required_exts
        self.extra_params = extra_params
        self.args = args
        self.llm = llm

        self.storage = LocalDuckdbStorage(
            llm=emb_llm,
            database_name="byzerai_store_duckdb.db",
            table_name="rag_duckdb",
            persist_dir=self.path,
            args=args,
        )
        self.queue = []
        self.chunk_size = 1000
        self.max_output_tokens = (
            extra_params.hybrid_index_max_output_tokens
        )

        # 设置缓存文件路径
        self.cache_dir = os.path.join(self.path, ".cache")
        self.cache_file = os.path.join(self.cache_dir,
                                       "duckdb_storage_speedup.jsonl")
        self.cache: Dict[str, CacheItem] = {}
        # 创建缓存目录
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # failed files support
        from .failed_files_utils import load_failed_files

        self.failed_files_path = os.path.join(
            self.cache_dir, "failed_files.json"
        )
        self.failed_files = load_failed_files(self.failed_files_path)

        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.process_queue)
        self.thread.daemon = True
        self.thread.start()

        # 加载缓存
        self.cache = self._load_cache()

    @staticmethod
    def _chunk_text(text, max_length=1000):
        """Split text into chunks"""
        chunks = []
        current_chunk = []
        current_length = 0

        for line in text.split("\n"):
            if current_length + len(line) > max_length and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(line)
            current_length += len(line)

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _load_cache(self) -> Dict[str, CacheItem]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    cache = {}
                    for line in lines:
                        try:
                            data = json.loads(line.strip())
                            if isinstance(data, dict) and "file_path" in data:
                                # 转换为 CacheItem 对象
                                cache_item = CacheItem.model_validate(data)
                                cache[data["file_path"]] = cache_item
                        except json.JSONDecodeError:
                            continue
                    return cache
            except Exception as e:
                logger.warning(f"Error loading cache file: {str(e)}")
                logger.exception(e)
                return {}
        return {}

    def write_cache(self):
        cache_file = self.cache_file

        if not fcntl:
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    for cache_item in self.cache.values():
                        # 确保序列化 Pydantic 模型
                        json.dump(cache_item.model_dump(), f, ensure_ascii=False)
                        f.write("\n")
            except IOError as e:
                logger.warning(f"Error writing cache file: {str(e)}")
                logger.exception(e)
        else:
            lock_file = cache_file + ".lock"
            with open(lock_file, "w", encoding="utf-8") as lockf:
                try:
                    # 获取文件锁
                    fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    # 写入缓存文件
                    with open(cache_file, "w", encoding="utf-8") as f:
                        for cache_item in self.cache.values():
                            # 确保序列化 Pydantic 模型
                            json.dump(cache_item.model_dump(), f, ensure_ascii=False)
                            f.write("\n")

                finally:
                    # 释放文件锁
                    fcntl.flock(lockf, fcntl.LOCK_UN)

    @staticmethod
    def fileinfo_to_tuple(file_info: FileInfo) -> Tuple[str, str, float, str]:
        return (
            file_info.file_path,
            file_info.relative_path,
            file_info.modify_time,
            file_info.file_md5,
        )

    def build_cache(self):
        """Build the cache by reading files and storing in DuckDBVectorStore"""
        logger.info(f"Building cache for path: {self.path}")

        files_to_process = []
        for file_info in self.get_all_files():
            if (
                file_info.file_path not in self.cache
                or self.cache[file_info.file_path].md5 != file_info.file_md5
            ):
                files_to_process.append(file_info)

        if not files_to_process:
            return

        from autocoder.rag.token_counter import initialize_tokenizer

        llm_name = get_llm_names(self.llm)[0] if self.llm else None
        product_mode = self.args.product_mode
        with Pool(
            processes=os.cpu_count(),
            initializer=initialize_tokenizer,
            initargs=(VariableHolder.TOKENIZER_PATH,),
        ) as pool:
            target_files_to_process = []
            for file_info in files_to_process:
                target_files_to_process.append(self.fileinfo_to_tuple(file_info))
            worker_func = functools.partial(
                process_file_in_multi_process, llm=llm_name, product_mode=product_mode
            )
            results = pool.map(worker_func, target_files_to_process)

        items = []
        for file_info, result in zip(files_to_process, results):
            content: List[SourceCode] = result
            self.cache[file_info.file_path] = CacheItem(
                file_path=file_info.file_path,
                relative_path=file_info.relative_path,
                content=[c.model_dump() for c in content],
                modify_time=file_info.modify_time,
                md5=file_info.file_md5,
            )

            for doc in content:
                logger.info(f"Processing file: {doc.module_name}")
                chunks = self._chunk_text(doc.source_code, self.chunk_size)
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_item = {
                        "_id": f"{doc.module_name}_{chunk_idx}",
                        "file_path": file_info.file_path,
                        "content": chunk,
                        "raw_content": chunk,
                        "vector": "",
                        "mtime": file_info.modify_time,
                    }
                    items.append(chunk_item)

        # Save to local cache
        logger.info("Saving cache to local file")
        self.write_cache()

        if items:
            logger.info("[BUILD CACHE] Clearing DuckDB Storage cache")
            self.storage.truncate_table()
            logger.info(f"[BUILD CACHE] Preparing to write to DuckDB Storage.")
            logger.info(
                f"[BUILD CACHE] Total chunks: {len(items)}, "
                f"Total files: {len(files_to_process)}"
            )

            # Use a fixed optimal batch size instead of dividing by worker count
            batch_size = 100  # Optimal batch size for Byzer Storage
            item_batches = [
                items[i : i + batch_size] for i in range(0, len(items), batch_size)
            ]

            total_batches = len(item_batches)
            completed_batches = 0

            logger.info(f"[BUILD CACHE] Writing to DuckDB Storage.")
            logger.info(
                f"[BUILD CACHE] Batch size: {batch_size}, "
                f"Total batches: {total_batches}"
            )
            start_time = time.time()

            # Use more workers to process the smaller batches efficiently
            max_workers = min(
                self.extra_params.rag_index_build_workers, total_batches
            )  # Cap at 10 workers or total batch count
            logger.info(
                f"[BUILD CACHE] Using {max_workers} parallel workers for processing"
            )

            def batch_add_doc(_batch):
                for b in _batch:
                    self.storage.add_doc(b, dim=self.extra_params.rag_duckdb_vector_dim)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                # Submit all batches to the executor upfront (non-blocking)
                for batch in item_batches:
                    futures.append(executor.submit(batch_add_doc, batch))

                # Wait for futures to complete
                for future in as_completed(futures):
                    try:
                        future.result()
                        completed_batches += 1
                        elapsed = time.time() - start_time
                        estimated_total = (
                            elapsed / completed_batches * total_batches
                            if completed_batches > 0
                            else 0
                        )
                        remaining = estimated_total - elapsed

                        # Only log progress at reasonable intervals to reduce log spam
                        if (
                            (completed_batches == 1)
                            or (completed_batches == total_batches)
                            or (completed_batches % max(1, total_batches // 10) == 0)
                        ):
                            progress_percent = (
                                completed_batches / total_batches * 100
                                if total_batches > 0
                                else 0
                            )
                            logger.info(
                                f"[BUILD CACHE] Progress: {completed_batches}/"
                                f"{total_batches} ({progress_percent:.1f}%). "
                                f"ETA: {remaining:.1f}s"
                            )
                    except Exception as e:
                        logger.error(f"[BUILD CACHE] Error saving batch: {str(e)}")
                        # Add more detailed error information
                        batch_len_info = (
                            len(batch) if "batch" in locals() else "unknown"
                        )
                        logger.error(
                            f"[BUILD CACHE] Error details: batch size: {batch_len_info}"
                        )
                        logger.exception(e)

            total_time = time.time() - start_time
            logger.info(
                f"[BUILD CACHE] All chunks written, total time: {total_time:.2f}s"
            )

    def update_storage(self, file_info: FileInfo, is_delete: bool):
        results = self.storage.query_by_path(file_info.file_path)
        if results:  # [('_id',)]
            for result in results:
                self.storage.delete_by_ids([result[0]])

        items = []
        if not is_delete:
            content = [
                SourceCode.model_validate(doc)
                for doc in self.cache[file_info.file_path].content
            ]
            modify_time = self.cache[file_info.file_path].modify_time
            for doc in content:
                logger.info(f"正在处理更新文件: {doc.module_name}")
                chunks = self._chunk_text(doc.source_code, self.chunk_size)
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_item = {
                        "_id": f"{doc.module_name}_{chunk_idx}",
                        "file_path": file_info.file_path,
                        "content": chunk,
                        "raw_content": chunk,
                        "vector": chunk,
                        "mtime": modify_time,
                    }
                    items.append(chunk_item)
        if items:
            for _chunk in items:
                try:
                    self.storage.add_doc(
                        _chunk, dim=self.extra_params.rag_duckdb_vector_dim
                    )
                    time.sleep(self.extra_params.anti_quota_limit)
                except Exception as err:
                    logger.error(f"Error in saving chunk: {str(err)}")
                    logger.exception(err)

    def process_queue(self):
        while self.queue:
            file_list = self.queue.pop(0)
            if isinstance(file_list, DeleteEvent):
                for item in file_list.file_paths:
                    logger.info(f"{item} is detected to be removed")
                    del self.cache[item]
                    # remove from failed files if present
                    if item in self.failed_files:
                        self.failed_files.remove(item)
                        save_failed_files(self.failed_files_path, self.failed_files)
                    # 创建一个临时的 FileInfo 对象
                    file_info = FileInfo(
                        file_path=item, relative_path="", modify_time=0, file_md5=""
                    )
                    self.update_storage(file_info, is_delete=True)

            elif isinstance(file_list, AddOrUpdateEvent):
                for file_info in file_list.file_infos:
                    logger.info(f"{file_info.file_path} is detected to be updated")
                    try:
                        content = process_file_local(
                            file_info.file_path,
                            llm=self.llm,
                            product_mode=self.product_mode,
                        )
                        if content:
                            self.cache[file_info.file_path] = CacheItem(
                                file_path=file_info.file_path,
                                relative_path=file_info.relative_path,
                                content=[c.model_dump() for c in content],
                                modify_time=file_info.modify_time,
                                md5=file_info.file_md5,
                            )
                            self.update_storage(file_info, is_delete=False)
                            # remove from failed files if present
                            if file_info.file_path in self.failed_files:
                                self.failed_files.remove(file_info.file_path)
                                save_failed_files(
                                    self.failed_files_path, self.failed_files
                                )
                        else:
                            logger.warning(
                                f"Empty result for file: {file_info.file_path}, treat as parse failed, skipping cache update"
                            )
                            self.failed_files.add(file_info.file_path)
                            save_failed_files(self.failed_files_path, self.failed_files)
                    except Exception as e:
                        logger.error(f"Error in process_queue: {str(e)}")
                        logger.exception(e)
                        self.failed_files.add(file_info.file_path)
                        save_failed_files(self.failed_files_path, self.failed_files)

            self.write_cache()

    def trigger_update(self):
        logger.info("检查文件是否有更新.....")
        files_to_process = []
        current_files = set()
        for file_info in self.get_all_files():
            current_files.add(file_info.file_path)
            # skip failed files
            if file_info.file_path in self.failed_files:
                logger.info(f"文件 {file_info.file_path} 之前解析失败，跳过此次更新")
                continue
            if (
                file_info.file_path not in self.cache
                or self.cache[file_info.file_path].md5 != file_info.file_md5
            ):
                files_to_process.append(file_info)

        deleted_files = set(self.cache.keys()) - current_files
        logger.info(f"待处理的文件: {len(files_to_process)}个")
        logger.info(f"已删除的文件: {len(deleted_files)}个")
        if deleted_files:
            with self.lock:
                self.queue.append(DeleteEvent(file_paths=deleted_files))
        if files_to_process:
            with self.lock:
                self.queue.append(AddOrUpdateEvent(file_infos=files_to_process))

    def get_all_files(self) -> List[FileInfo]:
        all_files = []
        for root, dirs, files in os.walk(self.path, followlinks=True):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in default_ignore_dirs
            ]

            if self.ignore_spec:
                relative_root = os.path.relpath(root, self.path)
                dirs[:] = [
                    d
                    for d in dirs
                    if not self.ignore_spec.match_file(os.path.join(relative_root, d))
                ]
                files = [
                    f
                    for f in files
                    if not self.ignore_spec.match_file(os.path.join(relative_root, f))
                ]

            for file in files:
                if self.required_exts and not any(
                    file.endswith(ext) for ext in self.required_exts
                ):
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.path)
                modify_time = os.path.getmtime(file_path)
                file_md5 = generate_file_md5(file_path)
                all_files.append(
                    FileInfo(
                        file_path=file_path,
                        relative_path=relative_path,
                        modify_time=modify_time,
                        file_md5=file_md5,
                    )
                )

        return all_files

    def _get_single_cache(
        self, query: str, options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        使用单个查询检索缓存文档

        参数:
            query: 查询字符串
            options: 包含查询选项的字典

        返回:
            包含文档信息的字典列表，每个字典包含_id、file_path、mtime和score字段
        """
        logger.info(f"正在使用向量搜索检索数据, 你的问题: {query}")
        results = []

        # Add vector search if enabled
        if options.get("enable_vector_search", True):
            # 返回值包含  [(_id, file_path, mtime, score,),]
            search_results = self.storage.vector_search(
                query,
                similarity_value=self.extra_params.rag_duckdb_query_similarity,
                similarity_top_k=self.extra_params.rag_duckdb_query_top_k,
                query_dim=self.extra_params.rag_duckdb_vector_dim,
            )

            # Convert tuples to dictionaries for the merger
            for _id, file_path, mtime, score in search_results:
                results.append(
                    {"_id": _id, "file_path": file_path, "mtime": mtime, "score": score}
                )

        logger.info(f"查询 '{query}' 返回 {len(results)} 条记录")
        return results

    def _process_search_results(self, results: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """
        处理搜索结果，提取文件路径并构建结果字典

        参数:
            results: 搜索结果列表，每项包含文档信息的字典

        返回:
            匹配文档的字典，键为文件路径，值为文件内容

        说明:
            该方法会根据查询结果从缓存中提取文件内容，并记录累计token数，
            当累计token数超过max_output_tokens时，将停止处理并返回已处理的结果。
        """
        # 记录被处理的总tokens数
        total_tokens = 0

        # Group results by file_path and reconstruct documents while preserving order
        # 这里还可以有排序优化，综合考虑一篇内容出现的次数以及排序位置
        file_paths = []
        seen = set()
        for result in results:
            file_path = result["file_path"]
            if file_path not in seen:
                seen.add(file_path)
                file_paths.append(file_path)

        # 从缓存中获取文件内容
        result = {}
        for file_path in file_paths:
            if file_path in self.cache:
                cached_data = self.cache[file_path]
                for doc in cached_data.content:
                    if total_tokens + doc["tokens"] > self.max_output_tokens:
                        logger.info(
                            f"当前检索已超出用户设置 Hybrid Index Max Tokens:"
                            f"{self.max_output_tokens}，累计tokens: {total_tokens}, "
                            f"经过向量搜索共检索出 {len(result.keys())} 个文档, "
                            f"共 {len(self.cache.keys())} 个文档"
                        )
                        return result
                    total_tokens += doc["tokens"]
                result[file_path] = cached_data.model_dump()
        logger.info(
            f"用户Hybrid Index Max Tokens设置为:{self.max_output_tokens}，"
            f"累计tokens: {total_tokens}, 经过向量搜索共检索出 "
            f"{len(result.keys())} 个文档, 共 {len(self.cache.keys())} 个文档"
        )
        return result

    def get_cache(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Dict]:
        """
        获取缓存中的文档信息

        参数:
            options: 包含查询参数的字典，可以包含以下键：
                - queries: 查询列表，可以是单个查询或多个查询
                - enable_vector_search: 是否启用向量搜索，默认为True
                - merge_strategy: 多查询时的合并策略，默认为WEIGHTED_RANK
                - max_results: 最大结果数，默认为None表示不限制

        返回:
            匹配文档的字典，键为文件路径，值为文件内容
        """
        self.trigger_update()  # 检查更新

        if options is None or "queries" not in options:
            return {
                file_path: self.cache[file_path].model_dump()
                for file_path in self.cache
            }

        queries = options.get("queries", [])

        # 如果没有查询或只有一个查询，使用原来的方法
        if not queries:
            return {
                file_path: self.cache[file_path].model_dump()
                for file_path in self.cache
            }
        elif len(queries) == 1:
            results = self._get_single_cache(queries[0], options)
            return self._process_search_results(results)

        # 导入合并策略
        from autocoder.rag.cache.cache_result_merge import (
            CacheResultMerger,
            MergeStrategy,
        )

        # 获取合并策略
        merge_strategy_name = options.get(
            "merge_strategy", MergeStrategy.WEIGHTED_RANK.value
        )
        try:
            merge_strategy = MergeStrategy(merge_strategy_name)
        except ValueError:
            logger.warning(
                f"未知的合并策略: {merge_strategy_name}, 使用默认策略 WEIGHTED_RANK"
            )
            merge_strategy = MergeStrategy.WEIGHTED_RANK

        # 限制最大结果数
        max_results = options.get("max_results", None)
        merger = CacheResultMerger(max_results=max_results)

        # 并发处理多个查询
        logger.info(
            f"处理多查询请求，查询数量: {len(queries)}, 合并策略: {merge_strategy}"
        )
        query_results = []
        with ThreadPoolExecutor(max_workers=min(len(queries), 10)) as executor:
            future_to_query = {
                executor.submit(self._get_single_cache, query, options): query
                for query in queries
            }
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    query_result = future.result()
                    logger.info(f"查询 '{query}' 返回 {len(query_result)} 条记录")
                    query_results.append((query, query_result))
                except Exception as e:
                    logger.error(f"处理查询 '{query}' 时出错: {str(e)}")
                    logger.exception(e)

        logger.info(f"所有查询共返回 {sum(len(r) for _, r in query_results)} 条记录")

        # 使用策略合并结果
        merged_results = merger.merge(query_results, strategy=merge_strategy)
        logger.info(f"合并后的结果共 {len(merged_results)} 条记录")

        # 处理合并后的结果
        return self._process_search_results(merged_results)
