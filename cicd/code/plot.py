import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import conducto as co


# Generate data.
print("Generating data")
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)

# Generate plot.
print("Generating plot")
fig, ax = plt.subplots()
ax.plot(t, s)
ax.set(xlabel="time (s)", ylabel="voltage (mV)", title="A Neat Plot")
ax.grid()

# Save plot to file.
filename = "/tmp/plot.png"
print(f"Saving plot to {filename}")
fig.savefig(filename)

# Put file in tempdata to get url for it.
co.temp_data.put(name="demo_plot", file=filename)
url = co.temp_data.url(name="demo_plot")
print(f"Plot at url={url}")

# Generate Markdown and reference plot by url.
print("Generating Markdown")
markdown = f"""<ConductoMarkdown>
One _very_ useful thing I can do is show a **plot**:
![plot]({url} "a neat plot")
</ConductoMarkdown>"""
print(markdown)
