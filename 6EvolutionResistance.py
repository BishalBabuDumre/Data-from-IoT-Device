import pandas as pd
import math
from sklearn.ensemble import IsolationForest
from datetime import date
from datetime import datetime
from datetime import timedelta
import numpy as np
import os
from pathlib import Path

#Getting yesterday's date
yesterday = date.today() - timedelta(days = 1)
yesterday = yesterday.strftime('%Y-%m-%d')

fNames = '101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,Keithley' # after move
fPath = os.path.join(Path.home(), 'SolarFarm/XML_Summary_As_CSV')
for fName in fNames.split(','):
    try:
        with open(os.path.join(Path.home(), 'SolarFarm/XML_Summary_As_CSV', fName, f'{yesterday}.csv')) as f:
            df = pd.read_csv(f)
            df['Series_Resistance'] = 0.0
            for index, row in df.iterrows():
                v = row["volts_curve"]
                i = row["amps_curve"]

                v = list(map(float, v[1:-1].split(",")))
                irev = list(map(float, i[1:-1].split(",")))
                i = [k*(-1) for k in irev]
                dvBYdi = []
                for k in range(1, len(v)):
                    if (i[k]-i[k-1])!=0.0:
                        dvsn = (v[k]-v[k-1])/(i[k]-i[k-1])
                    else:
                        dvsn = float('inf')
                    dvBYdi.append(dvsn)

                iPLUSiL = []
                for j in range(1, len(i)):
                    adsn = i[j]-i[0]
                    if adsn == 0:
                        invrs = float('inf')
                    else:
                        invrs = 1/adsn
                    iPLUSiL.append(invrs)

                inf_indices = [m for m, val in enumerate(dvBYdi) if math.isinf(val)]
                for n in sorted(inf_indices, reverse=True):
                    del dvBYdi[n]
                    del iPLUSiL[n]

                inf_indices = [m for m, val in enumerate(iPLUSiL) if math.isinf(val)]
                for n in sorted(inf_indices, reverse=True):
                    del dvBYdi[n]
                    del iPLUSiL[n]

                # Get indices of inliers (where resistance is between 0 and 300)
                inlier_indices = [i for i, x in enumerate(dvBYdi) if 0 <= x <= 300]
                # Filter both lists to keep only inliers
                resistance = [dvBYdi[q] for q in inlier_indices]
                current = [iPLUSiL[q] for q in inlier_indices]

                # Get indices of inliers (where current is between 0 and half of Isc.)
                z = 1/(irev[0]/2)
                inlier_indices = [i for i, x in enumerate(current) if 0 <= x <= z]
                # Filter both lists to keep only inliers
                resistance = [resistance[q] for q in inlier_indices]
                current = [current[q] for q in inlier_indices]

                X = np.array(resistance).reshape(-1, 1)
                if X.size > 0:
                    # Fit Isolation Forest and detect outliers
                    clf = IsolationForest(contamination='auto', random_state=42)
                    outliers = clf.fit_predict(X)  # Returns 1 for inliers, -1 for outliers

                    # Get indices of inliers (where outliers == 1)
                    inlier_indices = [i for i, x in enumerate(outliers) if x == 1]

                    # Filter both lists to keep only inliers
                    resistance = [resistance[q] for q in inlier_indices]
                    current = [current[q] for q in inlier_indices]

                    slope, intercept = np.polyfit(current, resistance, 1)
                    print(f"Slope: {slope}, Intercept: {intercept}")

                else:
                    intercept = float('inf')

                df.at[index, 'Series_Resistance'] = intercept
            df.to_csv(os.path.join(Path.home(), 'SolarFarm/XML_Summary_As_CSV', fName, f'{yesterday}.csv'), index=False)
    except FileNotFoundError:
        print(f"No file found.")
        continue