// Cloak 本地 HTTP API 最小示例（POST + JSON）。
using System.Net.Http.Json;
using System.Text.Json;

var baseUrl = (Environment.GetEnvironmentVariable("CLOAK_BASE_URL") ?? "http://127.0.0.1:54381").TrimEnd('/');
var cleanup = !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("CLOAK_CLEANUP"));

using var http = new HttpClient { BaseAddress = new Uri(baseUrl + "/") };
http.DefaultRequestHeaders.TryAddWithoutValidation("Content-Type", "application/json");

Console.WriteLine("Cloak API demo | base = " + baseUrl);

static void Print(string title, JsonElement el)
{
    Console.WriteLine("\n=== " + title + " ===");
    Console.WriteLine(JsonSerializer.Serialize(el, new JsonSerializerOptions { WriteIndented = true }));
}

async Task<JsonElement> Post(string path, object? body = null)
{
    var resp = await http.PostAsJsonAsync(path.TrimStart('/'), body ?? new { });
    resp.EnsureSuccessStatusCode();
    var doc = await JsonDocument.ParseAsync(await resp.Content.ReadAsStreamAsync());
    return doc.RootElement.Clone();
}

var r1 = await Post("group/list", new { });
Print("group_list", r1);

var groupName = "demo-csharp-" + DateTimeOffset.UtcNow.ToUnixTimeSeconds();
var r2 = await Post("group/add", new { groupName });
Print("group_add", r2);

string? groupId = null;
if (r2.TryGetProperty("success", out var ok) && ok.GetBoolean() &&
    r2.TryGetProperty("data", out var gd) && gd.TryGetProperty("id", out var gid))
    groupId = gid.GetString();

if (string.IsNullOrEmpty(groupId) && r1.TryGetProperty("data", out var d1) &&
    d1.TryGetProperty("list", out var list) && list.GetArrayLength() > 0)
{
    var first = list[0];
    if (first.TryGetProperty("id", out var id0))
        groupId = id0.GetString();
}

if (string.IsNullOrEmpty(groupId))
{
    Console.WriteLine("无法取得 groupId，退出");
    return;
}

var suffix = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
var r3 = await Post("browser/update", new
{
    name = "demo-browser-csharp-" + suffix,
    groupId,
    randomFingerprint = true,
    homepageUrl = "https://www.example.com"
});
Print("browser_update (create)", r3);

string? browserId = null;
if (r3.TryGetProperty("success", out var ok3) && ok3.GetBoolean() &&
    r3.TryGetProperty("data", out var bd) && bd.TryGetProperty("id", out var bid))
    browserId = bid.GetString();

var r4 = await Post("browser/list", new { page = 0, pageSize = 10 });
Print("browser_list", r4);

if (!string.IsNullOrEmpty(browserId))
{
    var r5 = await Post("browser/open", new { id = browserId });
    Print("browser_open", r5);
    var r6 = await Post("browser/close", new { id = browserId });
    Print("browser_close", r6);
}

if (cleanup && !string.IsNullOrEmpty(browserId))
{
    var r7 = await Post("browser/delete", new { id = browserId });
    Print("browser_delete", r7);
}
if (cleanup && !string.IsNullOrEmpty(groupId))
{
    var r8 = await Post("group/delete", new { id = groupId });
    Print("group_delete", r8);
}
