from ccd.procedures import fit_procedure as __determine_fit_procedure
import numpy as np
from ccd import app
import importlib
from .version import __version__
from .version import __algorithm__
from .version import __name

logger = app.logging.getLogger(__name)
defaults = app.defaults


def attr_from_str(value):
    """Returns a reference to the full qualified function, attribute or class.

    Args:
        value = Fully qualified path (e.g. 'ccd.models.lasso.fitted_model')

    Returns:
        A reference to the target attribute (e.g. fitted_model)
    """
    module, target = value.rsplit('.', 1)
    try:
        obj = importlib.import_module(module)
        return getattr(obj, target)
    except (ImportError, AttributeError) as e:
        logger.debug(e)
        return None


def __attach_metadata(procedure_results, procedure):
    """
    Attach some information on the algorithm version, what procedure was used,
    and which inputs were used

    Returns:
        A dict representing the change detection results

    {algorithm: 'pyccd:x.x.x',
     processing_mask: (bool, bool, ...),
     procedure: string,
     change_models: [
         {start_day: int,
          end_day: int,
          break_day: int,
          observation_count: int,
          change_probability: float,
          num_coefficients: int,
          blue:      {magnitude: float,
                     rmse: float,
                     coefficients: (float, float, ...),
                     intercept: float},
          green:    {magnitude: float,
                     rmse: float,
                     coefficients: (float, float, ...),
                     intercept: float},
          red:     {magnitude: float,
                     rmse: float,
                     coefficients: (float, float, ...),
                     intercept: float},
          nir:      {magnitude: float,
                     rmse: float,
                     coefficients: (float, float, ...),
                     intercept: float},
          swir1:    {magnitude: float,
                     rmse: float,
                     coefficients: (float, float, ...),
                     intercept: float},
          swir2:    {magnitude: float,
                     rmse: float,
                     coefficients: (float, float, ...),
                     intercept: float},
          thermal:  {magnitude: float,
                     rmse: float,
                     coefficients: (float, float, ...),
                     intercept: float}}
                    ]
    }
    """
    change_models, processing_mask = procedure_results

    return {'algorithm': __algorithm__,
            'processing_mask': processing_mask,
            'procedure': procedure.__name__,
            'change_modes': change_models}


def __split_dates_spectra(matrix):
    """ Slice the dates and spectra from the matrix and return """
    return matrix[0], matrix[1:7]


def detect(dates, reds, greens, blues, nirs,
           swir1s, swir2s, thermals, quality):
    """Entry point call to detect change

    No filtering up-front as different procedures may do things
    differently

    Args:
        dates:    1d-array or list of ordinal date values
        reds:     1d-array or list of red band values
        greens:   1d-array or list of green band values
        blues:    1d-array or list of blue band values
        nirs:     1d-array or list of nir band values
        swir1s:   1d-array or list of swir1 band values
        swir2s:   1d-array or list of swir2 band values
        thermals: 1d-array or list of thermal band values
        quality:  1d-array or list of qa band values

    Returns:
        Tuple of ccd.detections namedtuples
    """
    dates = np.asarray(dates)

    spectra = np.stack((reds, greens,
                        blues, nirs, swir1s,
                        swir2s, thermals))

    # load the fitter_fn from app.FITTER_FN
    fitter_fn = attr_from_str(defaults.FITTER_FN)

    # Determine which procedure to use for the detection
    procedure = __determine_fit_procedure(quality)

    # call detect and return results as the detections namedtuple
    return __attach_metadata(procedure(dates, spectra, fitter_fn, quality), procedure)
