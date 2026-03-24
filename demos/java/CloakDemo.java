import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;

/**
 * Cloak 本地 HTTP API 最小示例（POST + JSON）。需 Java 11+。
 */
public class CloakDemo {

    static String base() {
        String b = System.getenv().getOrDefault("CLOAK_BASE_URL", "http://127.0.0.1:54381");
        return b.endsWith("/") ? b.substring(0, b.length() - 1) : b;
    }

    static boolean cleanup() {
        return System.getenv("CLOAK_CLEANUP") != null && !System.getenv("CLOAK_CLEANUP").isEmpty();
    }

    static void print(String title, String json) {
        System.out.println("\n=== " + title + " ===");
        System.out.println(json);
    }

    static String post(HttpClient http, String path, String jsonBody) throws Exception {
        String url = base() + path;
        HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofSeconds(60))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody, StandardCharsets.UTF_8))
                .build();
        HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        if (resp.statusCode() < 200 || resp.statusCode() >= 300) {
            throw new RuntimeException("HTTP " + resp.statusCode() + ": " + resp.body());
        }
        return resp.body();
    }

    static String pickIdAfterSuccess(String responseJson, String idKey) {
        // 极简 JSON 取值：仅用于 demo；生产请使用 Jackson / Gson
        if (!responseJson.contains("\"success\":true") && !responseJson.contains("\"success\": true")) {
            return null;
        }
        String key = "\"" + idKey + "\"";
        int i = responseJson.indexOf(key);
        if (i < 0) {
            return null;
        }
        int colon = responseJson.indexOf(':', i);
        int q1 = responseJson.indexOf('"', colon + 1);
        int q2 = responseJson.indexOf('"', q1 + 1);
        if (q1 < 0 || q2 < 0) {
            return null;
        }
        return responseJson.substring(q1 + 1, q2);
    }

    static String firstGroupIdFromList(String groupListJson) {
        int idx = groupListJson.indexOf("\"list\"");
        if (idx < 0) {
            return null;
        }
        int idKey = groupListJson.indexOf("\"id\"", idx);
        if (idKey < 0) {
            return null;
        }
        int colon = groupListJson.indexOf(':', idKey);
        int q1 = groupListJson.indexOf('"', colon + 1);
        int q2 = groupListJson.indexOf('"', q1 + 1);
        if (q1 < 0 || q2 < 0) {
            return null;
        }
        return groupListJson.substring(q1 + 1, q2);
    }

    public static void main(String[] args) throws Exception {
        HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();
        System.out.println("Cloak API demo | base = " + base());

        String r1 = post(http, "/group/list", "{}");
        print("group_list", r1);

        String groupName = "demo-java-" + Instant.now().getEpochSecond();
        String r2 = post(http, "/group/add", "{\"groupName\":\"" + escapeJson(groupName) + "\"}");
        print("group_add", r2);

        String groupId = pickIdAfterSuccess(r2, "id");
        if (groupId == null) {
            groupId = firstGroupIdFromList(r1);
        }
        if (groupId == null) {
            System.out.println("无法取得 groupId，退出");
            return;
        }

        String suffix = String.valueOf(Instant.now().getEpochSecond());
        String bodyCreate = "{"
                + "\"name\":\"demo-browser-java-" + suffix + "\","
                + "\"groupId\":\"" + escapeJson(groupId) + "\","
                + "\"randomFingerprint\":true,"
                + "\"homepageUrl\":\"https://www.example.com\""
                + "}";
        String r3 = post(http, "/browser/update", bodyCreate);
        print("browser_update (create)", r3);

        String browserId = pickIdAfterSuccess(r3, "id");

        String r4 = post(http, "/browser/list", "{\"page\":0,\"pageSize\":10}");
        print("browser_list", r4);

        if (browserId != null) {
            String r5 = post(http, "/browser/open", "{\"id\":\"" + escapeJson(browserId) + "\"}");
            print("browser_open", r5);
            String r6 = post(http, "/browser/close", "{\"id\":\"" + escapeJson(browserId) + "\"}");
            print("browser_close", r6);
        }

        if (cleanup() && browserId != null) {
            String r7 = post(http, "/browser/delete", "{\"id\":\"" + escapeJson(browserId) + "\"}");
            print("browser_delete", r7);
        }
        if (cleanup()) {
            String r8 = post(http, "/group/delete", "{\"id\":\"" + escapeJson(groupId) + "\"}");
            print("group_delete", r8);
        }
    }

    static String escapeJson(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
