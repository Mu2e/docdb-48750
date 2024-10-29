# parameters for modifying original map data
# thermal noise
noise = 0.3 # Gauss
noise_str = '_noise'+str(noise).replace('.', 'p')
# phony curled field
phony_curl = 20.0 # Gauss / m
phony_curl_str = f'_curlZ'+str(phony_curl).replace('-', 'm').replace('.', 'p')
# x0 offset (center of DS)
x0 = -3.904
# z0 offest (center of DS)
z0 = 9.033
#z0 = 9.7 # Susan's number (middle after cutting out points) -- this is probably better.
# so we can create directory tree before dataframes are ready, need a minimal
# copy of the LSQ dir
LSQ_config_dict_minimal = {
    '1': {'subdir': '1_Nominal',
          'fitnames': {'Initial': 'fma_1_Nominal_fitmap', 'PINN_Subtracted': 'fma_1_Nominal_PINN_subtracted_fitmap'},
    },
    '2': {'subdir': '2_Traditional_PINN',
          'fitnames': {'Initial': 'fma_2_Traditional_PINN_fitmap', 'PINN_Subtracted': 'fma_2_Traditional_PINN_PINN_subtracted_fitmap'},
    },
    '3': {'subdir': '3_External_Fit',
          'fitnames': {'Initial': 'fma_3_External_Fit_fitmap', 'PINN_Subtracted': 'fma_3_External_Fit_PINN_subtracted_fitmap'},
    },
    '4': {'subdir': '4_Phony_Curl',
          'fitnames': {'Initial': 'fma_4_Phony_Curl_fitmap', 'PINN_Subtracted': 'fma_4_Phony_Curl_PINN_subtracted_fitmap'},
    },
    '5': {'subdir': '5_Nominal_CylSym',
          'fitnames': {'Initial': 'fma_5_Nominal_CylSym_fitmap', 'PINN_Subtracted': 'fma_5_Nominal_CylSym_PINN_subtracted_fitmap'},
    },
    '6': {'subdir': '6_Busbars_Only',
          'fitnames': {'Initial': 'fma_6_Busbars_Only_fitmap', 'PINN_Subtracted': 'fma_6_Busbars_Only_PINN_subtracted_fitmap'},
    },
    '7': {'subdir': '7_DSCoils_Only',
          'fitnames': {'Initial': 'fma_7_DSCoils_Only_fitmap', 'PINN_Subtracted': 'fma_7_DSCoils_Only_PINN_subtracted_fitmap'},
    },
}
