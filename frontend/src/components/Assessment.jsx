import React, { useState, useEffect, useRef } from 'react';

export default function Assessment({ onComplete }) {
  const [step, setStep] = useState('consent'); // 'consent', 'items', 'submitting'
  const [consentGiven, setConsentGiven] = useState(false);
  const [demographics, setDemographics] = useState({ age: 28, gender: 'Female', region: 'North' });
  const [assessmentId, setAssessmentId] = useState(null);
  const [items, setItems] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [responses, setResponses] = useState({});
  const [freeText, setFreeText] = useState({});
  
  // Timing & change tracking
  const itemStartTime = useRef(Date.now());
  const [changeCounts, setChangeCounts] = useState({});

  useEffect(() => {
    if (step === 'items') {
      itemStartTime.current = Date.now();
    }
  }, [currentIndex, step]);

  const handleStart = async () => {
    if (!consentGiven) return;
    try {
      const startRes = await fetch('http://localhost:8000/api/v1/assessment/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          consent_given: true,
          domain_variant: 'corporate',
          age: parseInt(demographics.age),
          gender: demographics.gender,
          region: demographics.region
        })
      });
      const startData = await startRes.json();
      setAssessmentId(startData.assessment_id);

      const itemsRes = await fetch('http://localhost:8000/api/v1/assessment/items');
      const itemsData = await itemsRes.json();
      setItems(itemsData);
      setStep('items');
    } catch (err) {
      console.error("Failed to start assessment:", err);
      alert("Error initializing assessment server.");
    }
  };

  const handleSelectOption = (itemId, optionId) => {
    const currentSelected = responses[itemId];
    if (currentSelected && currentSelected !== optionId) {
      setChangeCounts(prev => ({ ...prev, [itemId]: (prev[itemId] || 0) + 1 }));
    }
    setResponses(prev => ({ ...prev, [itemId]: optionId }));
  };

  const handleNextItem = () => {
    const currentItem = items[currentIndex];
    const latency = Date.now() - itemStartTime.current;

    // Record response metadata
    responses[`${currentItem.id}_latency`] = latency;

    if (currentIndex + 1 < items.length) {
      setCurrentIndex(prev => prev + 1);
    } else {
      handleSubmitAll();
    }
  };

  const handleSubmitAll = async () => {
    setStep('submitting');
    const submissionPayload = items.map(itm => ({
      item_id: itm.id,
      selected_option: responses[itm.id] || 'A',
      latency_ms: responses[`${itm.id}_latency`] || 3500.0,
      answer_change_count: changeCounts[itm.id] || 0,
      free_text_justification: freeText[itm.id] || ''
    }));

    try {
      const res = await fetch('http://localhost:8000/api/v1/assessment/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assessment_id: assessmentId,
          responses: submissionPayload,
          self_report_proxy: {
            Conscientiousness: 0.78,
            "Emotional Stability": 0.72,
            Agreeableness: 0.75,
            Extraversion: 0.65,
            Openness: 0.80
          }
        })
      });
      const data = await res.json();
      onComplete(assessmentId);
    } catch (err) {
      console.error("Submission failed:", err);
      alert("Error submitting assessment.");
    }
  };

  if (step === 'consent') {
    return (
      <div style={{ maxWidth: '650px', margin: '4rem auto' }} className="glass-card">
        <h2 style={{ fontSize: '1.75rem', marginBottom: '1rem', color: '#6366f1' }}>Project Mapan</h2>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>AI-Assisted Occupational Fit Assessment</h3>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
          This assessment evaluates situational behavior and personality trait alignment for corporate roles.
          Under India's Digital Personal Data Protection (DPDP) framework, your responses will be used strictly for research evaluation and demo fit scoring.
        </p>

        <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={consentGiven}
              onChange={e => setConsentGiven(e.target.checked)}
              style={{ width: '18px', height: '18px' }}
            />
            <span>I give informed consent to participate in this scenario assessment.</span>
          </label>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Age</label>
            <input
              type="number"
              value={demographics.age}
              onChange={e => setDemographics({ ...demographics, age: e.target.value })}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: 'white' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Gender</label>
            <select
              value={demographics.gender}
              onChange={e => setDemographics({ ...demographics, gender: e.target.value })}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: 'white' }}
            >
              <option value="Female">Female</option>
              <option value="Male">Male</option>
              <option value="Non-binary">Non-binary</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Region</label>
            <input
              type="text"
              value={demographics.region}
              onChange={e => setDemographics({ ...demographics, region: e.target.value })}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: 'white' }}
            />
          </div>
        </div>

        <button
          className="btn-primary"
          style={{ width: '100%', justifyContent: 'center', opacity: consentGiven ? 1 : 0.5 }}
          disabled={!consentGiven}
          onClick={handleStart}
        >
          Begin Assessment
        </button>
      </div>
    );
  }

  if (step === 'submitting') {
    return (
      <div style={{ textAlign: 'center', margin: '6rem auto' }} className="glass-card">
        <h3>Processing Psychometric & NLP Pipeline...</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Fusing CTT, IRT, Response Latency, and NLP Trait Embeddings</p>
      </div>
    );
  }

  const currentItem = items[currentIndex];

  return (
    <div style={{ maxWidth: '800px', margin: '3rem auto' }} className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <span className="badge badge-info">Scenario {currentIndex + 1} of {items.length}</span>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Target Trait: {currentItem.target_trait}</span>
      </div>

      <h3 style={{ fontSize: '1.35rem', marginBottom: '0.75rem', color: '#38bdf8' }}>{currentItem.scenario_title}</h3>
      <p style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', lineHeight: '1.6' }}>
        {currentItem.scenario_narrative}
      </p>

      <h4 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>{currentItem.prompt}</h4>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
        {currentItem.options.map(opt => (
          <div
            key={opt.id}
            onClick={() => handleSelectOption(currentItem.id, opt.id)}
            style={{
              padding: '1rem',
              borderRadius: '8px',
              border: responses[currentItem.id] === opt.id ? '2px solid #6366f1' : '1px solid #334155',
              background: responses[currentItem.id] === opt.id ? 'rgba(99, 102, 241, 0.15)' : 'rgba(15, 23, 42, 0.6)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem'
            }}
          >
            <span style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: responses[currentItem.id] === opt.id ? '#6366f1' : '#334155',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              fontSize: '0.9rem'
            }}>
              {opt.id}
            </span>
            <span>{opt.text}</span>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem' }}>
          Free-text Justification (Optional NLP Embedding Input):
        </label>
        <textarea
          rows={3}
          value={freeText[currentItem.id] || ''}
          onChange={e => setFreeText({ ...freeText, [currentItem.id]: e.target.value })}
          placeholder="Explain the reasoning behind your choice..."
          style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: '#0f172a', border: '1px solid #334155', color: 'white', resize: 'vertical' }}
        />
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button
          className="btn-primary"
          onClick={handleNextItem}
          disabled={!responses[currentItem.id]}
          style={{ opacity: responses[currentItem.id] ? 1 : 0.5 }}
        >
          {currentIndex + 1 === items.length ? 'Submit Assessment' : 'Next Scenario'}
        </button>
      </div>
    </div>
  );
}
