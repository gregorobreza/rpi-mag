import numpy as np
import matplotlib.pyplot as plt

data = np.load("test.npz")

freq = data["freq"]
H1 = data["H1"]
H2 = data["H2"]
coh = data["coh"]

sel = (freq>0) & (freq<40000)

# plt.semilogy(freq[sel], np.abs(H1[sel]))
# plt.semilogy(freq[sel], np.abs(H2[sel]))
#plt.plot(freq[sel], np.angle(H1[sel]))
plt.plot(freq[sel], np.abs(coh[sel]))
plt.savefig("dummy_name.png")

f_min = 0
f_max = 10000

sel = (freq>f_min) & (freq<f_max)

fig, [ax1, ax2, ax3]  = plt.subplots(3,1, sharex=True)
ax1.plot(freq[sel], 20*np.log10(np.abs(H1[11][sel])))
ax2.plot(fr[sel], np.angle(H1[11][sel], deg=1))
ax3.plot(fr[sel], np.abs(coh[11][sel]))

ax3.set_xlabel('f [Hz]')
ax2.set_ylabel('Kot [°]')
ax3.set_ylabel('Koherenca')
ax1.set_ylabel('Amplituda [dB]')