const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");
const axios = require("axios");
const xml2js = require("xml2js");
const crypto = require("crypto");

const OPENSRS_USERNAME = process.env.OPENSRS_USERNAME;
const OPENSRS_API_KEY = process.env.OPENSRS_API_KEY;
const OPENSRS_ENDPOINT = process.env.OPENSRS_ENDPOINT || "https://rr-n1-tor.opensrs.net:55443/";

if (!OPENSRS_USERNAME || !OPENSRS_API_KEY) {
  console.error("Missing OPENSRS_USERNAME or OPENSRS_API_KEY in environment.");
  process.exit(1);
}

const server = new Server(
  { name: "opensrs-mcp", version: "2.0.0" },
  { capabilities: { tools: {} } }
);

function generateSignature(xml, apiKey) {
  const hash1 = crypto.createHash("md5").update(xml + apiKey).digest("hex");
  return crypto.createHash("md5").update(hash1 + apiKey).digest("hex");
}

function kvItem(key, value) {
  if (Array.isArray(value)) return { $: { key }, dt_array: [{ item: value }] };
  if (value && typeof value === "object") {
    return {
      $: { key },
      dt_assoc: [{ item: Object.entries(value).map(([k, v]) => kvItem(k, v)) }],
    };
  }
  return { $: { key }, _: value == null ? "" : String(value) };
}

function toEnvelopeXml(object, action, attributes = {}) {
  const builder = new xml2js.Builder({ rootName: "OPS_envelope", headless: false, renderOpts: { pretty: false } });
  const payload = {
    header: { version: "0.9" },
    body: {
      data_block: {
        dt_assoc: {
          item: [
            { $: { key: "protocol" }, _: "XCP" },
            { $: { key: "object" }, _: object },
            { $: { key: "action" }, _: action },
            kvItem("attributes", attributes),
          ],
        },
      },
    },
  };
  return builder.buildObject(payload);
}

function parseItems(xmlObj) {
  const items = xmlObj?.OPS_envelope?.body?.[0]?.data_block?.[0]?.dt_assoc?.[0]?.item || [];
  const out = {};
  for (const it of items) {
    const k = it?.$?.key;
    if (!k) continue;
    if (it._ != null) out[k] = it._;
    else if (it.dt_assoc) out[k] = it.dt_assoc[0];
    else if (it.dt_array) out[k] = it.dt_array[0];
    else out[k] = it;
  }
  return out;
}

function dtAssocToObject(dtAssocNode) {
  const items = dtAssocNode?.item || [];
  const out = {};
  for (const it of items) {
    const k = it?.$?.key;
    if (!k) continue;
    if (it._ != null) out[k] = it._;
    else if (it.dt_assoc) out[k] = dtAssocToObject(it.dt_assoc[0]);
    else if (it.dt_array) out[k] = (it.dt_array[0]?.item || []).map((entry) => {
      if (entry._ != null) return entry._;
      if (entry.dt_assoc) return dtAssocToObject(entry.dt_assoc[0]);
      return entry;
    });
  }
  return out;
}

async function opensrsRequest(object, action, attributes = {}) {
  const xml = toEnvelopeXml(object, action, attributes);
  const signature = generateSignature(xml, OPENSRS_API_KEY);
  const response = await axios.post(OPENSRS_ENDPOINT, xml, {
    headers: {
      "Content-Type": "text/xml",
      "X-Username": OPENSRS_USERNAME,
      "X-Signature": signature,
    },
    timeout: 70000,
  });

  const parsed = await xml2js.parseStringPromise(response.data);
  const top = parseItems(parsed);
  const code = Number(top.response_code || 0);
  const ok = String(top.is_success || "0") === "1";

  if (!ok) {
    throw new Error(`OpenSRS ${code}: ${top.response_text || "Unknown error"}`);
  }

  return {
    raw: parsed,
    response_code: code,
    response_text: top.response_text || "",
    attributes: top.attributes ? dtAssocToObject(top.attributes) : {},
  };
}

function extractARecords(attributes) {
  const records = attributes?.records || {};
  const list = Array.isArray(records.A) ? records.A : [];
  return list.map((r) => ({ subdomain: r.subdomain || "", ip_address: r.ip_address || "" }));
}

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "opensrs_get_balance",
      description: "Get OpenSRS reseller balance",
      inputSchema: { type: "object", properties: {}, additionalProperties: false },
    },
    {
      name: "opensrs_list_domains",
      description: "List reseller domains by expiration date window",
      inputSchema: {
        type: "object",
        properties: {
          exp_from: { type: "string", description: "YYYY-MM-DD" },
          exp_to: { type: "string", description: "YYYY-MM-DD" },
          limit: { type: "integer", default: 100 },
        },
        required: ["exp_from", "exp_to"],
        additionalProperties: false,
      },
    },
    {
      name: "opensrs_get_dns_zone",
      description: "Get DNS zone records for a domain",
      inputSchema: {
        type: "object",
        properties: { domain: { type: "string" } },
        required: ["domain"],
        additionalProperties: false,
      },
    },
    {
      name: "opensrs_upsert_a_record",
      description: "Upsert an A record in OpenSRS DNS zone (preserves all existing records)",
      inputSchema: {
        type: "object",
        properties: {
          domain: { type: "string" },
          subdomain: { type: "string", description: "Use empty string for root (@)" },
          ip_address: { type: "string" },
        },
        required: ["domain", "subdomain", "ip_address"],
        additionalProperties: false,
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args = {} } = request.params;

  try {
    if (name === "opensrs_get_balance") {
      const res = await opensrsRequest("reseller", "get_balance", {});
      return { content: [{ type: "text", text: JSON.stringify(res.attributes, null, 2) }] };
    }

    if (name === "opensrs_list_domains") {
      const res = await opensrsRequest("domain", "get_domains_by_expiredate", {
        exp_from: args.exp_from,
        exp_to: args.exp_to,
        limit: args.limit ?? 100,
      });
      return { content: [{ type: "text", text: JSON.stringify(res.attributes, null, 2) }] };
    }

    if (name === "opensrs_get_dns_zone") {
      const res = await opensrsRequest("domain", "get_dns_zone", { domain: args.domain });
      return { content: [{ type: "text", text: JSON.stringify(res.attributes, null, 2) }] };
    }

    if (name === "opensrs_upsert_a_record") {
      const zone = await opensrsRequest("domain", "get_dns_zone", { domain: args.domain });
      const attrs = zone.attributes;
      const records = attrs.records || {};
      const aRecords = extractARecords(attrs);

      const idx = aRecords.findIndex((r) => (r.subdomain || "") === (args.subdomain || ""));
      const nextA = [...aRecords];
      if (idx >= 0) nextA[idx] = { subdomain: args.subdomain || "", ip_address: args.ip_address };
      else nextA.push({ subdomain: args.subdomain || "", ip_address: args.ip_address });

      const nextRecords = { ...records, A: nextA };
      await opensrsRequest("domain", "set_dns_zone", {
        domain: args.domain,
        records: nextRecords,
      });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ ok: true, domain: args.domain, subdomain: args.subdomain || "@", ip_address: args.ip_address }, null, 2),
          },
        ],
      };
    }

    throw new Error(`Tool not found: ${name}`);
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`OpenSRS MCP ready (${OPENSRS_ENDPOINT})`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
