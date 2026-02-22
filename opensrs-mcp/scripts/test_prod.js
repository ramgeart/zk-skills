const axios = require("axios");
const xml2js = require("xml2js");
const crypto = require("crypto");

const USER = process.env.OPENSRS_USERNAME;
const KEY = process.env.OPENSRS_API_KEY;
const ENDPOINT = process.env.OPENSRS_ENDPOINT || "https://rr-n1-tor.opensrs.net:55443/";

if (!USER || !KEY) {
  console.error("Set OPENSRS_USERNAME and OPENSRS_API_KEY");
  process.exit(1);
}

function sig(xml) {
  const h1 = crypto.createHash("md5").update(xml + KEY).digest("hex");
  return crypto.createHash("md5").update(h1 + KEY).digest("hex");
}

function item(key, value) {
  if (Array.isArray(value)) return { $: { key }, dt_array: [{ item: value }] };
  if (value && typeof value === "object") {
    return { $: { key }, dt_assoc: [{ item: Object.entries(value).map(([k, v]) => item(k, v)) }] };
  }
  return { $: { key }, _: String(value ?? "") };
}

async function req(object, action, attributes = {}) {
  const builder = new xml2js.Builder({ rootName: "OPS_envelope", renderOpts: { pretty: false } });
  const xml = builder.buildObject({
    header: { version: "0.9" },
    body: {
      data_block: {
        dt_assoc: {
          item: [
            { $: { key: "protocol" }, _: "XCP" },
            { $: { key: "object" }, _: object },
            { $: { key: "action" }, _: action },
            item("attributes", attributes),
          ],
        },
      },
    },
  });

  const r = await axios.post(ENDPOINT, xml, {
    headers: { "Content-Type": "text/xml", "X-Username": USER, "X-Signature": sig(xml) },
    timeout: 70000,
  });
  return xml2js.parseStringPromise(r.data);
}

(async () => {
  const bal = await req("reseller", "get_balance", {});
  console.log("get_balance OK");

  const domains = await req("domain", "get_domains_by_expiredate", {
    exp_from: "2026-01-01",
    exp_to: "2030-12-31",
    limit: 100,
  });
  console.log("get_domains_by_expiredate OK");

  const zone = await req("domain", "get_dns_zone", { domain: "zkarmor.com" });
  console.log("get_dns_zone OK");

  console.log(JSON.stringify({ bal, domains, zone }, null, 2).slice(0, 4000));
})();
