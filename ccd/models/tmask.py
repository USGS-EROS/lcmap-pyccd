import numpy as np

from ccd.models.robust_fit import RLM


def tmask_coefficient_matrix(dates, avg_days_yr):
    """Coefficient matrix that is used for Tmask modeling

    Args:
        dates: list of ordinal julian dates

    Returns:
        Populated numpy array with coefficient values
    """
    annual_cycle = 2*np.pi/avg_days_yr
    observation_cycle = annual_cycle / np.ceil((dates[-1] - dates[0]) / avg_days_yr)

    ac_dates = annual_cycle * dates
    oc_dates = observation_cycle * dates

    matrix = np.ones(shape=(dates.shape[0], 5), order='F')
    matrix[:, 0] = np.cos(ac_dates)
    matrix[:, 1] = np.sin(ac_dates)
    matrix[:, 2] = np.cos(oc_dates)
    matrix[:, 3] = np.sin(oc_dates)
    #print("** matrix: {} {}".format(matrix.ndim, matrix.dtype))
    return matrix


def tmask(dates,
          observations,
          variogram,
          bands,
          t_const,
          avg_days_yr):
    """Produce an index for filtering outliers.

    Arguments:
        dates: ordinal date values associated to each n-moment in the
            observations
        observations: spectral values, assumed to be shaped as
            (n-bands, n-moments)
        bands: list of band indices used for outlier detection, by default
            it's the green and SWIR1 bands.
        t_const: constant used to scale a variogram value for thresholding on
            whether a value is an outlier or not

    Return: indexed array, excluding outlier observations.
    """
    # variogram = calculate_variogram(observations)
    # Time and expected values using a four-part matrix of coefficients.
    # regression = lm.LinearRegression()

    tmask_matrix = tmask_coefficient_matrix(dates, avg_days_yr)

    #print("tmask_matrix {} {} {}".format(type(tmask_matrix), tmask_matrix.ndim, tmask_matrix.dtype))
    # Accumulator for outliers. This starts off as a list of False values
    # because we don't assume anything is an outlier.
    #_, sample_count = observations.shape[0]
    sample_count = observations.shape[1]
    #print("sample_count {} ".format(type(sample_count)))
    outliers = np.zeros(sample_count, dtype=bool)
    #print("outliers {} {} {}".format(type(outliers), outliers.ndim, outliers.dtype))

    # For each band, determine if the delta between predicted and actual
    # values exceeds the threshold. If it does, then it is an outlier.
    #regression_fit = regression.fit
    for band_ix in bands:
        # TODO this needs to be configurable.
        fit = RLM(maxiter=5).fit(tmask_matrix, observations[band_ix])
        predicted = fit.predict(tmask_matrix)
        outliers += np.abs(predicted - observations[band_ix]) > variogram[band_ix] * t_const

    # Keep all observations that aren't outliers.
    return outliers
    # return dates[~outliers], observations[:, ~outliers]
