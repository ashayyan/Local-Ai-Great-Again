using System.Diagnostics;
using System.Text.Json;

int warmup = GetInt("--warmup", 2);
int reps = GetInt("--repetitions", 7);
int mib = GetInt("--mib", 256);
int threads = GetInt("--threads", 1);
if (warmup < 0 || reps < 1 || mib < 1 || threads < 1) throw new ArgumentException("warmup >= 0, repetitions >= 1, mib >= 1 required");
int n = checked(mib * 1024 * 1024 / sizeof(double));
var a = new double[n]; var b = new double[n]; var c = new double[n];
for (int i = 0; i < n; i++) { a[i] = 1.0; b[i] = 2.0; c[i] = 0.0; }
GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
for (int i = 0; i < warmup; i++) { RunParallel(a,b,c,threads); GC.KeepAlive(c); }
var samples = new List<double>(reps);
for (int i = 0; i < reps; i++) {
    var sw = Stopwatch.StartNew(); RunParallel(a,b,c,threads); sw.Stop();
    GC.KeepAlive(c);
    double seconds = sw.Elapsed.TotalSeconds;
    double mibPerSec = 3.0 * mib / seconds; // STREAM Triad reads A/B and writes C: 3 x array footprint.
    samples.Add(mibPerSec);
    Console.WriteLine(JsonSerializer.Serialize(new { type="sample", repetition=i+1, seconds, mib_per_sec=mibPerSec }));
}
samples.Sort();
double median = samples.Count % 2 == 1 ? samples[samples.Count/2] : (samples[samples.Count/2-1]+samples[samples.Count/2])/2.0;
Console.WriteLine(JsonSerializer.Serialize(new { type="summary", operation="triad", array_mib=mib, arrays=3, warmup, repetitions=reps, raw_mib_per_sec=samples, median_mib_per_sec=median, checksum=c[0] + c[n/2] + c[n-1], dotnet=Environment.Version.ToString(), os=Environment.OSVersion.ToString(), processor=Environment.GetEnvironmentVariable("PROCESSOR_IDENTIFIER") ?? "unknown" }));

static void Run(double[] a, double[] b, double[] c) {
    const double scalar = 3.0;
    for (int i = 0; i < c.Length; i++) c[i] = a[i] + scalar * b[i];
}
static void RunParallel(double[] a, double[] b, double[] c, int threads) {
    const double scalar = 3.0;
    Parallel.For(0, threads, t => { int start = c.Length * t / threads; int end = c.Length * (t + 1) / threads; for (int i = start; i < end; i++) c[i] = a[i] + scalar * b[i]; });
}
static int GetInt(string name, int fallback) {
    var args = Environment.GetCommandLineArgs();
    for (int i=0; i<args.Length-1; i++) if (args[i].Equals(name, StringComparison.OrdinalIgnoreCase) && int.TryParse(args[i+1], out var v)) return v;
    return fallback;
}
