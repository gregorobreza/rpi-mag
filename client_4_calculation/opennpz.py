import numpy as np
import matplotlib.pyplot as plt

data = np.load("test.npz")

input = data["input"]
output = data["output"]
freq = data["freq"]
H1 = data["H1"]
H2 = data["H2"]
coh = data["coh"]

f_min = 0
f_max = 20000

sel = (freq>f_min) & (freq<f_max)

# plt.semilogy(freq[sel], np.abs(H1[sel]))
# plt.semilogy(freq[sel], np.abs(H2[sel]))
#plt.plot(freq[sel], np.angle(H1[sel]))
# plt.plot(freq[sel], np.abs(coh[sel]))
# plt.savefig("dummy_name.png")



fig, [ax1, ax2, ax3]  = plt.subplots(3,1, sharex=True)
ax1.plot(freq[sel], 20*np.log10(np.abs(H1[sel])))
ax2.plot(freq[sel], np.angle(H1[sel], deg=1))
ax3.plot(freq[sel], np.abs(coh[sel]))

ax3.set_xlabel('f [Hz]')
ax2.set_ylabel('Kot [°]')
ax3.set_ylabel('Koherenca')
ax1.set_ylabel('Amplituda [dB]')

plt.savefig("dummy_name.png")