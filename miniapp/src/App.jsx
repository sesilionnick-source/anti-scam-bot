import { useState, useEffect } from 'react'
 
const API_BASE = 'http://localhost:8000'
 
function truncateAddress(addr) {
  if (!addr || addr.length < 12) return addr
  return addr.slice(0, 6) + '...' + addr.slice(-4)
}
 
function getRiskColors(level) {
  if (level === 'LOW RISK') return { bg: '#052e16', border: '#166534', score: '#22c55e', badge: '#22c55e', badgeText: '#052e16' }
  if (level === 'MEDIUM RISK') return { bg: '#451a03', border: '#92400e', score: '#f59e0b', badge: '#f59e0b', badgeText: '#451a03' }
  return { bg: '#450a0a', border: '#991b1b', score: '#ef4444', badge: '#ef4444', badgeText: '#450a0a' }
}
 
function ShieldIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      <polyline points="9 12 11 14 15 10"/>
    </svg>
  )
}
 
function WarningIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  )
}
 
function Spinner() {
  return (
    <div className="spinner-wrap">
      <div className="spinner" />
      <span className="spinner-text">Analyzing token...</span>
    </div>
  )
}
 
function DisclaimerScreen({ onAgree }) {
  const [checked, setChecked] = useState(false)
  return (
    <div className="screen">
      <div className="disclaimer-header">
        <WarningIcon />
        <h1 className="disclaimer-title">Terms of Use</h1>
        <p className="disclaimer-subtitle">Please read carefully before proceeding</p>
      </div>
      <div className="disclaimer-card">
        <div className="disclaimer-section">
          <div className="disclaimer-section-title">No Financial Advice</div>
          <p className="disclaimer-section-text">This tool provides heuristic-based analysis of on-chain data and smart contract bytecode only. It does not constitute financial advice, investment advice, or any other form of professional advice.</p>
        </div>
        <div className="disclaimer-divider" />
        <div className="disclaimer-section">
          <div className="disclaimer-section-title">No Liability</div>
          <p className="disclaimer-section-text">The developer accepts no liability whatsoever for any financial losses, investment decisions, or any other outcomes arising from the use of this tool. You use this tool entirely at your own risk.</p>
        </div>
        <div className="disclaimer-divider" />
        <div className="disclaimer-section">
          <div className="disclaimer-section-title">Limitations</div>
          <p className="disclaimer-section-text">Analysis is heuristic-based and may be incomplete, inaccurate, or outdated. A LOW RISK result does not guarantee token safety. Always conduct independent research before any transaction.</p>
        </div>
        <div className="disclaimer-divider" />
        <div className="disclaimer-section">
          <div className="disclaimer-section-title">Cryptocurrency Risk</div>
          <p className="disclaimer-section-text">All cryptocurrency transactions carry significant financial risk including total loss of funds. Never invest more than you can afford to lose.</p>
        </div>
      </div>
      <label className="checkbox-row">
        <input type="checkbox" checked={checked} onChange={e => setChecked(e.target.checked)} className="checkbox-input" />
        <span className="checkbox-label">I have read and agree to the terms above. I understand this tool does not provide financial advice and I use it at my own risk.</span>
      </label>
      <button className="agree-btn" disabled={!checked} onClick={onAgree}>I Agree — Continue</button>
      <p className="hint-text">You must accept the terms to use this tool</p>
    </div>
  )
}
 
function InputScreen({ onResult }) {
  const [address, setAddress] = useState('')
  const [network, setNetwork] = useState('bsc')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
 
  async function handleAnalyze() {
    if (!address.trim()) return
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/analyze?token=${address.trim()}&network=${network}`)
      const data = await res.json()
      if (!res.ok || data.error) {
        setError(data.error || 'Analysis failed. Check the address and try again.')
      } else {
        onResult(data)
      }
    } catch {
      setError('Could not reach the server. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }
 
  return (
    <div className="screen">
      <div className="input-header">
        <ShieldIcon />
        <h1 className="app-title">Token Risk Checker</h1>
        <p className="app-subtitle">Paste a token contract address to analyze</p>
      </div>
      <div className="card">
        <label className="field-label">Token address</label>
        <input className="address-input" type="text" placeholder="0x..." value={address} onChange={e => setAddress(e.target.value)} spellCheck={false} autoComplete="off" />
      </div>
      <div className="card">
        <label className="field-label">Network</label>
        <div className="network-toggle">
          <button className={`net-btn ${network === 'bsc' ? 'active' : ''}`} onClick={() => setNetwork('bsc')}>BSC</button>
          <button className={`net-btn ${network === 'eth' ? 'active' : ''}`} onClick={() => setNetwork('eth')}>ETH</button>
        </div>
      </div>
      {error && <div className="error-card"><span className="error-icon">⚠</span><span>{error}</span></div>}
      {loading ? <Spinner /> : (
        <button className="analyze-btn" onClick={handleAnalyze} disabled={!address.trim() || loading}>Analyze token</button>
      )}
      <p className="hint-text">Supports Ethereum and Binance Smart Chain</p>
    </div>
  )
}
 
function ResultRow({ label, value, valueClass }) {
  return (
    <div className="result-row">
      <span className="row-label">{label}</span>
      <span className={`row-value ${valueClass || ''}`}>{value}</span>
    </div>
  )
}
 
function yesNoUnknown(val) {
  if (val === true) return { text: 'Yes', cls: 'val-yes' }
  if (val === false) return { text: 'No', cls: 'val-no' }
  return { text: 'Unknown', cls: 'val-unknown' }
}
 
function ResultScreen({ data, onBack }) {
  const { token, contract_analysis, liquidity_analysis, final_assessment } = data
  const colors = getRiskColors(final_assessment.risk_level)
  const ownerVal = yesNoUnknown(contract_analysis.owner_present)
  const mintVal = contract_analysis.mint_function_present ? { text: 'Detected', cls: 'val-danger' } : { text: 'Not found', cls: 'val-no' }
  const liqVal = yesNoUnknown(liquidity_analysis.has_liquidity)
 
  return (
    <div className="screen">
      <button className="back-btn" onClick={onBack}>← Back</button>
      <div className="risk-header" style={{ background: colors.bg, borderColor: colors.border }}>
        <span className="risk-badge" style={{ background: colors.badge, color: colors.badgeText }}>{final_assessment.risk_level}</span>
        <div className="risk-score" style={{ color: colors.score }}>{final_assessment.risk_score}<span className="score-max">/100</span></div>
        <div className="token-name">{token.name} <span className="token-symbol">({token.symbol})</span></div>
      </div>
      <div className="card">
        <div className="card-title">Contract details</div>
        <ResultRow label="Address" value={truncateAddress(token.address)} />
        <ResultRow label="Network" value={token.network.toUpperCase()} />
        <ResultRow label="Owner" value={ownerVal.text} valueClass={ownerVal.cls} />
        <ResultRow label="Mint function" value={mintVal.text} valueClass={mintVal.cls} />
        <div className="result-row">
          <span className="row-label">Patterns</span>
          <span className={`row-value ${contract_analysis.suspicious_patterns.length > 0 ? 'val-danger' : 'val-no'}`}>
            {contract_analysis.suspicious_patterns.length > 0 ? contract_analysis.suspicious_patterns.join(', ') : 'None detected'}
          </span>
        </div>
      </div>
      <div className="card">
        <div className="card-title">Liquidity</div>
        <ResultRow label="DEX" value={liquidity_analysis.dex || 'Unknown'} />
        <ResultRow label="Status" value={liquidity_analysis.status} />
        <ResultRow label="Has liquidity" value={liqVal.text} valueClass={liqVal.cls} />
      </div>
      <div className="card">
        <div className="card-title">Risk factors</div>
        {final_assessment.reasons.length === 0 ? (
          <p className="val-no" style={{ margin: 0, fontSize: 13 }}>No major risk factors detected</p>
        ) : (
          final_assessment.reasons.map((r, i) => (
            <div key={i} className="risk-factor"><span className="factor-dot" /><span>{r}</span></div>
          ))
        )}
      </div>
      <div className="card">
        <div className="card-title">Recommendation</div>
        <p className="recommendation-text">{final_assessment.recommendation}</p>
      </div>
      <div className="disclaimer">
        This tool provides heuristic-based analysis only. It does not constitute financial advice.
        The developer accepts no liability for any financial losses. Use at your own risk.
      </div>
    </div>
  )
}
 
export default function App() {
  const [agreed, setAgreed] = useState(false)
  const [result, setResult] = useState(null)
 
  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready()
      window.Telegram.WebApp.expand()
    }
    const saved = sessionStorage.getItem('terms_agreed')
    if (saved === 'true') setAgreed(true)
  }, [])
 
  function handleAgree() {
    sessionStorage.setItem('terms_agreed', 'true')
    setAgreed(true)
  }
 
  if (!agreed) return <div className="app"><DisclaimerScreen onAgree={handleAgree} /></div>
 
  return (
    <div className="app">
      {result ? <ResultScreen data={result} onBack={() => setResult(null)} /> : <InputScreen onResult={setResult} />}
    </div>
  )
}