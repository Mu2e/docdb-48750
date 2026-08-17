import os
import sys
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
from LSQ_configs import LSQ_config_dict

### model plots
# common plots to start
#plots_for_all =  [f'{B}_RZ_Z4.200_Z13.900_Phi{phi}_{fit}_heat.pdf' for B in ['Br', 'Bphi', 'Bz'] for phi in ['0.00'] for fit in ['LSQfit', 'PINNfit', 'LSQ2fit', 'FullModel']]
plots_for_all =  [f'{B}_RZ_Z4.200_Z13.900_Phi{phi}_{fit}_heat.pdf' for B in ['Br', 'Bphi', 'Bz'] for phi in ['0.00'] for fit in ['LSQfit', 'PINNfit', 'FullModel']]
plots_for_all += ['logLoss_vs_Epoch.pdf', 'residual_dBz_1D_hist_df_test.pdf', 'residual_dBz_1D_hist_df_meas.pdf', 'NN_dBz_vs_Z_X_m0p8_Y_0p0.pdf', 'NN_dBz_vs_X_Y_0p0_Z_8p4.pdf', 'NN_dBr_vs_Z_X_m0p8_Y_0p0.pdf', 'NN_dBphi_vs_Z_X_m0p8_Y_0p0.pdf']

model_plots_for_paper = {}
for model_num in LSQ_config_dict.keys():
    model_plots_for_paper[model_num] = [f'{model_num}_'+p for p in plots_for_all]

# additions
# 1: more cohesive set of plots
model_plots_for_paper['1'] += ['1_LR_vs_Epoch.pdf', '1_lambda_vs_Epoch.pdf', '1_residual_dBr_1D_hist_df_test.pdf', '1_residual_dBphi_1D_hist_df_test.pdf', '1_residual_dBr_1D_hist_df_meas.pdf', '1_residual_dBphi_1D_hist_df_meas.pdf', '1_derivs_curlB_z_1D_hist_with_numerical_with_exact_df_test.pdf', '1_derivs_divB_1D_hist_with_numerical_with_exact_df_test.pdf', '1_NN_dBz_vs_Z_X_0p8_Y_0p0.pdf', '1_wb_plot.pdf', '1_wb_plot_logy.pdf']
model_plots_for_paper['1'] += [f'1_{B}_RZ_Z4.200_Z13.900_Phi{phi}_{fit}_heat.pdf' for B in ['Br', 'Bphi', 'Bz'] for phi in ['0.00'] for fit in ['LSQ2fit']]
model_plots_for_paper['1'] += [f'1_{B}_RZ_Z4.200_Z13.900_Phi{phi}_{fit}_heat.pdf' for B in ['Br', 'Bphi', 'Bz'] for phi in ['1.57'] for fit in ['FullModel']]
# 2: div + curl, for comparison to 1
model_plots_for_paper['2'] += ['2_derivs_curlB_z_1D_hist_with_numerical_with_exact_df_test.pdf', '2_derivs_divB_1D_hist_with_numerical_with_exact_df_test.pdf']
# 3: external fit
# 4: Bphi profile is interesting to show along with Bz
model_plots_for_paper['4'] += ['4_NN_dBphi_vs_Z_X_m0p8_Y_0p0.pdf']
# 8: HPC mag unc
model_plots_for_paper['8'] += ['8_residual_dBr_1D_hist_df_test.pdf', '8_residual_dBphi_1D_hist_df_test.pdf', '8_residual_dBr_1D_hist_df_meas.pdf', '8_residual_dBphi_1D_hist_df_meas.pdf']
# 9: sparser measurements
model_plots_for_paper['9'] += ['9_residual_dBr_1D_hist_df_test.pdf', '9_residual_dBphi_1D_hist_df_test.pdf', '9_residual_dBr_1D_hist_df_meas.pdf', '9_residual_dBphi_1D_hist_df_meas.pdf']
