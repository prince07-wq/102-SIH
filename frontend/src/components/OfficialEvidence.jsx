import { useEffect, useRef, useState } from 'react';
import { getApiAssetUrl, getProjectEvidence } from '../services/api';

export default function OfficialEvidence({ projectId }) {
  const [state, setState] = useState('idle');
  const [evidence, setEvidence] = useState(null);
  const [error, setError] = useState(null);
  const requestController = useRef(null);

  useEffect(() => () => requestController.current?.abort(), []);

  async function checkEvidence() {
    requestController.current?.abort();
    const controller = new AbortController();
    requestController.current = controller;
    setState('loading');
    setError(null);

    try {
      const result = await getProjectEvidence(projectId, controller.signal);
      setEvidence(result);
      setState('complete');
    } catch (requestError) {
      if (requestError.name === 'AbortError') return;
      setError(requestError.message);
      setEvidence(null);
      setState('failed');
    }
  }

  const status = evidence?.status;
  const processingFailed = state === 'failed' || status === 'PROCESSING_FAILED';
  const hasPhotos = status === 'PHOTO_GPS' || status === 'PHOTO_ONLY';
  const originalDocuments = (evidence?.attachments || []).filter(
    (attachment) => attachment.original_url,
  );

  return (
    <section className="pd__section pd__official-evidence" aria-busy={state === 'loading'}>
      <div className="pd__evidence-heading">
        <div>
          <h3 className="panel-title">Official Evidence</h3>
          <p>Attachments are retrieved from official MPLADS records only when requested.</p>
        </div>
        {evidence?.cached && <span className="pd__evidence-cache">Cached result</span>}
      </div>

      {state === 'idle' && (
        <button type="button" className="pd__evidence-button" onClick={checkEvidence}>
          Check Official Evidence
        </button>
      )}

      {state === 'loading' && (
        <p className="pd__evidence-loading">Checking official project records...</p>
      )}

      {hasPhotos && (
        <div className="pd__evidence-result">
          <h4>View On-Site Progress</h4>
          <div className="pd__evidence-photos">
            {evidence.photos.map((photo, index) => (
              <a
                href={getApiAssetUrl(photo.url)}
                target="_blank"
                rel="noreferrer"
                key={`${photo.attachment_id}-${photo.source_page || 0}-${index}`}
              >
                <img
                  src={getApiAssetUrl(photo.url)}
                  alt={`Official on-site progress attachment ${index + 1}`}
                  loading="lazy"
                />
              </a>
            ))}
          </div>
          {(evidence.latitude !== null ||
            evidence.longitude !== null ||
            evidence.location_text ||
            evidence.timestamp) && (
            <div className="pd__evidence-location">
              {evidence.latitude !== null && evidence.longitude !== null && (
                <span className="mono">
                  {evidence.latitude}, {evidence.longitude}
                </span>
              )}
              {evidence.location_text && <span>{evidence.location_text}</span>}
              {evidence.timestamp && <span>Captured: {evidence.timestamp}</span>}
            </div>
          )}
        </div>
      )}

      {status === 'DOCUMENT_ONLY' && (
        <div className="pd__evidence-result">
          <p>No on-site photo found in available records</p>
          <h4>View Official Documents</h4>
        </div>
      )}

      {status === 'NO_ATTACHMENT' && (
        <p className="pd__evidence-empty">No official evidence attachment available.</p>
      )}

      {processingFailed && (
        <div className="pd__evidence-error">
          <p>{error || 'Official evidence could not be processed at this time.'}</p>
          <button type="button" className="pd__evidence-button" onClick={checkEvidence}>
            Retry Official Evidence Check
          </button>
        </div>
      )}

      {state === 'complete' && originalDocuments.length > 0 && (
        <div className="pd__evidence-documents">
          {status !== 'DOCUMENT_ONLY' && <h4>Official Documents</h4>}
          {originalDocuments.map((attachment) => (
            <a
              href={getApiAssetUrl(attachment.original_url)}
              target="_blank"
              rel="noreferrer"
              key={attachment.attachment_id}
            >
              {attachment.original_file_name || 'View official document'}
            </a>
          ))}
        </div>
      )}
    </section>
  );
}
