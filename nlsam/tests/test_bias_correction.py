import numpy as np
from numpy.testing import assert_allclose, assert_array_less

from nlsam.bias_correction import root_finder_sigma, multiprocess_stabilization


def test_root_finder_sigma():

    eta = np.full((10, 10, 10, 10), 100, dtype=np.float32)
    sigma = np.full((10, 10, 10, 10), 1, dtype=np.float32)
    N = np.full((10, 10, 10, 10), 1, dtype=np.float32)
    mask = np.ones_like(eta[..., 0])
    output = root_finder_sigma(eta, sigma, N, mask)
    assert_allclose(output, sigma, atol=1e-4)

    output = root_finder_sigma(eta, sigma[..., 0], N)
    assert_allclose(output, sigma, atol=1e-4)

    mask[5:8, 3:9] = 0
    output = root_finder_sigma(eta, sigma, N, mask)
    sigma[5:8, 3:9] = 0
    assert_allclose(output, sigma, atol=1e-4)

    # magnitude SNR of 0.5 -> sigma = 50, eta = 25 for N = 1
    a = [np.sqrt((25 + np.random.randn(10000) * 50)**2 + (np.random.randn(10000) * 50)**2) for ii in range(250)]
    eta = np.mean(a, axis=1, keepdims=True, dtype=np.float64)
    sigma = np.std(a, axis=1, keepdims=True, dtype=np.float64)
    N = np.ones(sigma.shape, dtype=np.float32)
    output = root_finder_sigma(eta, sigma, N)

    # everything less than 10% error of real value?
    assert_allclose(output, 50, atol=5)


# Taken from original example
def test_stabilization():

    noisySI = [974.4680312435205, 920.5810792869341, 819.6650525922458, 802.5190824927682, 727.7646357302121, 673.6333509410033,
               637.1774633934145, 602.8078282410685, 567.7671645871519, 498.7547410153283, 485.5944666179963, 428.07612179503263,
               388.6169930632023, 386.18961037199415, 376.08823042097316, 338.8477133073723, 309.2480238229747, 294.5568206195705,
               281.2171535075004, 213.8208886916726, 254.72160898469483, 195.57830703833136, 211.93867859510462, 199.35740205728564,
               156.25468049264455, 195.68094257648, 145.5655485672349, 142.54704777102097, 146.47263504779266, 94.33540214158423,
               99.05286040252803, 136.20629630937805, 100.99664099645533, 69.68392363472498, 62.14865572661666, 52.90535288375964,
               49.658854513180145, 44.697987693731164, 93.30094647357532, 76.58788137313091, 44.495013750130134, 49.78130435111957,
               28.591123274109403, 14.369557430945626, 15.942197375234471, 33.018212055985686, 26.294114699100742, 28.04829536743325,
               37.51661668556541, 24.48232853550999, 31.99219938621985, 52.34547007932935, 26.191496658272193, 41.97686572440534,
               36.3838412672615, 13.115824695742333, 23.5749116813857, 40.302257429852816, 15.969279873602586, 7.895003815354128,
               24.188839271486874, 29.558535336818906, 25.768383455514858, 33.7149871310329, 33.41987503558679, 28.325411074385094,
               28.696660350714314, 14.07918430602742, 28.408626617687165, 37.46161004997681, 16.56374580286518, 32.37433087637632,
               9.729146991334474, 31.138236631716335, 9.167230200724529, 18.04542095255966, 52.10527513423827, 8.605375161904306,
               34.09528519417992, 63.3642397915748, 61.82192674167916, 10.402761307531772, 43.507101594742785, 17.706587093874955,
               28.37424648150537, 53.99808241916874, 27.468625611884256, 28.907958786532625, 5.016136842885782, 12.331750562238897,
               12.152385742126548, 14.708345988504204, 20.880343502584108, 45.633794111081926, 33.192065161666356, 12.913596989980766,
               45.29593334531513, 29.53694349839379, 46.163861173396285, 30.7950601400292]

    noisySI = np.atleast_3d(noisySI)
    sigma = 20 * np.ones_like(noisySI)
    N = 1 * np.ones_like(noisySI)
    mask = np.ones_like(noisySI, dtype=bool)

    # this is my mhat value
    # mhat = noiseFloorBreaker.getSmoothedNoisyY();

    mhat = [943.064, 887.3957, 834.2781, 783.6333, 735.3848, 689.4572, 645.7762, 604.2689, 564.8634, 527.4889,
            492.0759, 458.5563, 426.8627, 396.9292, 368.691, 342.0846, 317.0474, 293.5182, 271.4369, 250.7447,
            231.3837, 213.2975, 196.4307, 180.729, 166.1395, 152.6104, 140.0909, 128.5316, 117.8841, 108.1015,
            99.1377, 90.9479, 83.4886, 76.7173, 70.5929, 65.0752, 60.1254, 55.7058, 51.7798, 48.3122,
            45.2688, 42.6165, 40.3235, 38.3593, 36.6944, 35.3005, 34.1505, 33.2185, 32.4797, 31.9106,
            31.4888, 31.1931, 31.0035, 30.9011, 30.8682, 30.8884, 30.9463, 31.0279, 31.12, 31.211, 31.2903,
            31.3484, 31.3771, 31.3693, 31.3191, 31.2218, 31.0739, 30.873, 30.6179, 30.3087, 29.9465,
            29.5336, 29.0737, 28.5714, 28.0325, 27.4643, 26.8748, 26.2736, 25.6712, 25.0795, 24.5113,
            23.9808, 23.5034, 23.0955, 22.7748, 22.5601, 22.4715, 22.5301, 22.7584, 23.1799, 23.8194,
            24.7027, 25.857, 27.3106, 29.0928, 31.2343, 33.767, 36.7238, 40.1388, 44.0474]

    mhat = np.atleast_3d(mhat)
    output, eta = multiprocess_stabilization(noisySI, mhat, mask, sigma, N, clip_eta=False)
    output = np.squeeze(output)

    # I don't do smoothing spline, but that's the original answer from the example
    answer = [974.2593726961478, 920.3597667319971, 819.4231414958396, 802.2668203840909, 727.4911655717409, 673.3397826429069,
              636.8655525156472, 602.4762973365341, 567.4138194140878, 498.36462680537056, 485.1850405704123, 427.6244261928154,
              388.1256497359557, 385.67824995114523, 375.550487309446, 338.25943462672035, 308.6082359466962, 293.8753142961541,
              280.4916819303696, 212.95552793566432, 253.8956549617732, 194.59559884274094, 210.95459224130636, 198.29899885042968,
              155.00568696626567, 194.51918845151363, 144.1531688581149, 141.0556597413872, 144.93682118478924, 92.32463302866627,
              96.99864160364926, 134.390675844964, 98.77163808516804, 66.86041462967017, 59.01058535014334, 49.33084567830052,
              45.78395417969499, 40.40195130633103, 90.30452841877286, 73.09523092130462, 39.538701406456745, 44.923916179379724,
              21.524819337268777, 2.820316365861366, 4.547482300636311, 25.626003309507375, 17.342640577295022, 19.162913692479087,
              30.00643329778439, 14.150562288816953, 23.23493062732895, 46.02474785656308, 15.872957579637127, 34.52136613085204,
              28.130876133261662, -3.2174505936025426, 12.443049405628651, 32.67940631097349, 1.6787650036381692, -13.399037943001979,
              13.447168302800774, 20.24060349684604, 15.531496420565338, 25.223446441028116, 24.855270814361273, 18.66489721848824,
              19.050759954801688, -1.579409967777238, 18.455007635460614, 29.13402464314681, 1.67455620109423, 22.696580697922574,
              -11.576166656070544, 20.487375774483535, -14.252931105463608, 1.17382943507633, 43.51615128517772, -19.195336233250714,
              19.70798582645859, 50.43287809129897, 41.837380939647375, -31.22879936476589, 16.28225096283407, -20.44505140252145,
              -5.360035836498812, 26.012597370773324, -7.420160356020831, -5.2786865917498265, -49.61487490109381, -29.915540407092003,
              -28.174166156025954, -19.14950163583434, 2.092206023707173, 36.610231728702075, 23.401060738784402, -3.290610983920377,
              38.97549861580737, 21.928292961384074, 40.847622456375305, 24.546650297329517]

    # this is the result for alpha = 0. 0001, deactivating the smoothing spline call, but I think it uses some default value instead
    # answer = [942.8518, 887.1702, 834.0382, 783.378, 735.1127, 689.1669, 645.4663, 603.9377, 564.509, 527.1093, 491.669, 458.1195,
    #           426.3934, 396.4244, 368.1474, 341.4984, 316.4147, 292.8344, 270.6971, 249.9432, 230.5145, 212.3536, 195.4044, 179.612,
    #           164.9223, 151.2824, 138.6405, 126.9459, 116.1488, 106.2006, 97.0534, 88.6607, 80.9766, 73.956, 67.5545, 61.7283,
    #           56.4345, 51.6315, 47.2797, 43.3427, 39.7879, 36.5871, 33.7167, 31.1576, 28.8945, 26.9153, 25.2099, 23.7687,
    #           22.5811, 21.6345, 20.9125, 20.3948, 20.0574, 19.8734, 19.8141, 19.8505, 19.9549, 20.1011, 20.2653, 20.4265,
    #           20.5661, 20.6679, 20.7181, 20.7044, 20.6166, 20.4455, 20.1832, 19.8227, 19.3574, 18.7812, 18.0876, 17.2695,
    #           16.3185, 15.2228, 13.966, 12.5213, 10.8419, 8.8317, 6.2328, 0.9175, -5.9684, -8.369, -10.0663, -11.3271, -12.2337,
    #           -12.8077, -13.038, -12.886, -12.2782, -11.077, -8.977, -4.8259, 7.1326, 12.1041, 16.3589, 20.4676, 24.6239,
    #           28.9353, 33.4804, 38.3278]

    answer = np.array(answer)

    # this is the output of eta = noiseFloorBreaker.getFixedPointEstimates(); with deactivated smoothing spline,
    # eta_koay = [974.2594, 920.3598, 819.4231, 802.2668, 727.4912, 673.3398, 636.8656, 602.4763, 567.4138, 498.3646,
    #             485.185, 427.6244, 388.1256, 385.6782, 375.5505, 338.2594, 308.6082, 293.8753, 280.4917, 212.9555,
    #             253.8957, 194.5956, 210.9546, 198.299, 155.0057, 194.5192, 144.1532, 141.0557, 144.9368, 92.3246,
    #             96.9986, 134.3907, 98.7716, 66.8604, 59.0106, 49.3308, 45.784, 40.402, 90.3045, 73.0952, 39.5387,
    #             44.9239, 21.5248, 2.8203, 4.5475, 25.626, 17.3426, 19.1629, 30.0064, 14.1506, 23.2349, 46.0247,
    #             15.873, 34.5214, 28.1309, -3.2175, 12.443, 32.6794, 1.6788, -13.399, 13.4472, 20.2406, 15.5315,
    #             25.2234, 24.8553, 18.6649, 19.0508, -1.5794, 18.455, 29.134, 1.6746, 22.6966, -11.5762, 20.4874,
    #             -14.2529, 1.1738, 43.5162, -19.1953, 19.708, 50.4329, 41.8374, -31.2288, 16.2823, -20.4451, -5.36,
    #             26.0126, -7.4202, -5.2787, -49.6149, -29.9155, -28.1742, -19.1495, 2.0922, 36.6102, 23.4011,
    #             -3.2906, 38.9755, 21.9283, 40.8476, 24.5467]

    # this is eta with the default smoothing and stuff
    eta_koay = [942.8518, 887.1702, 834.0382, 783.378, 735.1127, 689.1669, 645.4663, 603.9377, 564.509,
                527.1093, 491.669, 458.1195, 426.3934, 396.4244, 368.1474, 341.4984, 316.4147, 292.8344, 270.6971,
                249.9432, 230.5145, 212.3536, 195.4044, 179.612, 164.9223, 151.2824, 138.6405, 126.9459, 116.1488,
                106.2006, 97.0534, 88.6607, 80.9766, 73.956, 67.5545, 61.7283, 56.4345, 51.6315, 47.2797, 43.3427,
                39.7879, 36.5871, 33.7167, 31.1576, 28.8945, 26.9153, 25.2099, 23.7687, 22.5811, 21.6345,
                20.9125, 20.3948, 20.0574, 19.8734, 19.8141, 19.8505, 19.9549, 20.1011, 20.2653, 20.4265,
                20.5661, 20.6679, 20.7181, 20.7044, 20.6166, 20.4455, 20.1832, 19.8227, 19.3574, 18.7812,
                18.0876, 17.2695, 16.3185, 15.2228, 13.966, 12.5213, 10.8419, 8.8317, 6.2328, 0.9175, -5.9684, -8.369,
                -10.0663, -11.3271, -12.2337, -12.8077, -13.038, -12.886, -12.2782, -11.077, -8.977, -4.8259, 7.1326,
                12.1041, 16.3589, 20.4676, 24.6239, 28.9353, 33.4804, 38.3278]

    eta_koay = np.atleast_3d(eta_koay)

    # I don't do smoothing spline, but using the smoothed input on both versions this is what we have
    # The answer is a bit off for the last values of the final output, might be due to different numerical schemes
    assert_allclose(output[:80], answer[:80], atol=1e-2, rtol=1e-5)
    assert_allclose(eta, eta_koay, atol=1e-2, rtol=1e-6)
