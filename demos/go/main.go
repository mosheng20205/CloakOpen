// Cloak 本地 HTTP API 最小示例（POST + JSON）。
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"time"
)

func getenv(key, def string) string {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	return v
}

func post(base, path string, body any) (map[string]any, error) {
	b, err := json.Marshal(body)
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequest(http.MethodPost, base+path, bytes.NewReader(b))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var out map[string]any
	dec := json.NewDecoder(resp.Body)
	if err := dec.Decode(&out); err != nil {
		return nil, err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return out, fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	return out, nil
}

func printResult(title string, m map[string]any) {
	fmt.Printf("\n=== %s ===\n", title)
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	_ = enc.Encode(m)
}

func main() {
	base := getenv("CLOAK_BASE_URL", "http://127.0.0.1:54381")
	if len(base) > 0 && base[len(base)-1] == '/' {
		base = base[:len(base)-1]
	}
	cleanup := os.Getenv("CLOAK_CLEANUP") != ""

	fmt.Println("Cloak API demo | base =", base)

	r1, err := post(base, "/group/list", map[string]any{})
	if err != nil {
		panic(err)
	}
	printResult("group_list", r1)

	groupName := "demo-go-" + strconv.FormatInt(time.Now().Unix(), 10)
	r2, err := post(base, "/group/add", map[string]any{"groupName": groupName})
	if err != nil {
		panic(err)
	}
	printResult("group_add", r2)

	var groupID string
	if v, ok := r2["success"].(bool); ok && v {
		if data, ok := r2["data"].(map[string]any); ok && data != nil {
			if id, ok := data["id"].(string); ok {
				groupID = id
			}
		}
	}
	if groupID == "" {
		if data, ok := r1["data"].(map[string]any); ok && data != nil {
			if list, ok := data["list"].([]any); ok && len(list) > 0 {
				if first, ok := list[0].(map[string]any); ok {
					if id, ok := first["id"].(string); ok {
						groupID = id
					}
				}
			}
		}
	}
	if groupID == "" {
		fmt.Println("无法取得 groupId，退出")
		return
	}

	suffix := strconv.FormatInt(time.Now().Unix(), 10)
	r3, err := post(base, "/browser/update", map[string]any{
		"name":               "demo-browser-go-" + suffix,
		"groupId":            groupID,
		"randomFingerprint":  true,
		"homepageUrl":        "https://www.example.com",
	})
	if err != nil {
		panic(err)
	}
	printResult("browser_update (create)", r3)

	var browserID string
	if v, ok := r3["success"].(bool); ok && v {
		if data, ok := r3["data"].(map[string]any); ok && data != nil {
			if id, ok := data["id"].(string); ok {
				browserID = id
			}
		}
	}

	r4, err := post(base, "/browser/list", map[string]any{"page": 0, "pageSize": 10})
	if err != nil {
		panic(err)
	}
	printResult("browser_list", r4)

	if browserID != "" {
		r5, err := post(base, "/browser/open", map[string]any{"id": browserID})
		if err != nil {
			panic(err)
		}
		printResult("browser_open", r5)
		r6, err := post(base, "/browser/close", map[string]any{"id": browserID})
		if err != nil {
			panic(err)
		}
		printResult("browser_close", r6)
	}

	if cleanup && browserID != "" {
		r7, err := post(base, "/browser/delete", map[string]any{"id": browserID})
		if err != nil {
			panic(err)
		}
		printResult("browser_delete", r7)
	}
	if cleanup && groupID != "" {
		r8, err := post(base, "/group/delete", map[string]any{"id": groupID})
		if err != nil {
			panic(err)
		}
		printResult("group_delete", r8)
	}
}
