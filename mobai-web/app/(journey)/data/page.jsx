"use client";

import { Plus, Lock, ChevronRight } from "lucide-react";
import consumer from "@/app/data/consumer.json";
import Reveal from "@/components/visual/Reveal";
import CountUp from "@/components/visual/CountUp";

const zhSent = Object.fromEntries(consumer.platformSentiment.map((p) => [p.platform, p]));

export default function DataPage() {
  return (
    <>
      <section className="jsection">
        <p className="section-eyebrow">Social listening</p>
        <h1 className="jtitle">Where the engine listens</h1>
        <p className="jlead">
          The engine is fed by public social conversation in the two languages most relevant to the product. English comes
          from Twitter for a broad global signal; Chinese comes from Xiaohongshu, Weibo, and Douyin for the primary China
          market. The same six analytical dimensions are applied to every platform so findings stay comparable.
        </p>
      </section>

      <Reveal>
        <section className="jsection">
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
            <h2 className="jsubhead" style={{ margin: 0 }}>Connected data sources</h2>
            <span className="chart-caption" style={{ margin: 0 }}>
              <CountUp to={consumer.corpusTotal} /> posts, 2 languages, 4 platforms
            </span>
          </div>
          <div className="source-grid" style={{ marginTop: 16 }} data-tour="sources">
            {consumer.corpus.map((c) => (
              <div className="source-card" key={c.platform}>
                <div className="src-head">
                  <span className="src-name">{c.platform}</span>
                  <span className="src-lang">{c.language}</span>
                </div>
                <span className="src-count"><CountUp to={c.posts} /></span>
                <span className="live-dot"><i />connected{zhSent[c.platform] ? ` (${zhSent[c.platform].pos}% positive)` : ""}</span>
                <span className="src-role">{c.role}</span>
              </div>
            ))}
            <div className="source-card locked" aria-disabled="true">
              <Lock size={18} color="#f7f1e678" style={{ margin: "0 auto" }} />
              <span className="src-name"><Plus size={13} style={{ verticalAlign: "-2px" }} /> Connect a new source</span>
              <span className="lock-note">The engine is source-agnostic. Only the datasets above are available in this demo build.</span>
            </div>
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection">
          <h2 className="jsubhead">How the data is pulled and prepared</h2>
          <div className="pipe-flow" style={{ marginBottom: 14 }}>
            <span className="pf"><strong>Scrape</strong> per platform</span>
            <span className="pf-arrow"><ChevronRight size={16} strokeWidth={2.2} aria-hidden="true" /></span>
            <span className="pf">Clean, <strong>dedupe</strong>, relevance filter</span>
            <span className="pf-arrow"><ChevronRight size={16} strokeWidth={2.2} aria-hidden="true" /></span>
            <span className="pf"><strong>Sentiment</strong> and entities</span>
            <span className="pf-arrow"><ChevronRight size={16} strokeWidth={2.2} aria-hidden="true" /></span>
            <span className="pf"><strong>Segment</strong></span>
          </div>
          <p className="jbody">
            Collection is organised around six structured query groups. English is collected with an authenticated Twitter
            scraper; Chinese is collected with self-hosted crawlers and managed actors across Xiaohongshu, Weibo, and
            Douyin. Each post is retained with its metadata, author identifiers are hashed so no personal identity is
            stored, and Chinese posts that mention no protein or beverage term are removed by a relevance filter.
          </p>
          <div className="note" style={{ marginTop: 14 }}>
            <strong>Dual-model sentiment.</strong> Sentiment is scored on original-language text with a consensus routed by
            language: VADER and TextBlob for English, a RoBERTa Chinese model and SnowNLP for Chinese. The final score is
            the average of the two models, and a confidence value is one minus their absolute difference, so posts where
            both models agree are weighted more heavily.
          </div>
        </section>
      </Reveal>
    </>
  );
}
