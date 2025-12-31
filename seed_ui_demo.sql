-- === 1) 모델 API Key 테이블 =========================================
-- UI: "새 API Key 등록" 팝업 대응
CREATE TABLE IF NOT EXISTS model_api_key (
  id             BIGSERIAL PRIMARY KEY,
  alias          VARCHAR(100) NOT NULL,  -- 별칭 (예: TEST_API_Key)
  provider_code  VARCHAR(50)  NOT NULL,  -- 제공자 코드 (예: openai)
  model          VARCHAR(100) NOT NULL,  -- 모델명 (예: gpt-5-nano)
  endpoint_url   VARCHAR(255) NOT NULL,  -- 엔드포인트 URL
  usage_code     VARCHAR(50)  NOT NULL,  -- 용도 코드 (예: chat, embed 등)
  api_key        TEXT         NOT NULL,  -- 실제 키(여기는 더미 값)
  is_public      BOOLEAN      NOT NULL DEFAULT FALSE, -- 공개 키 토글
  is_enabled     BOOLEAN      NOT NULL DEFAULT TRUE,  -- 활성화 토글
  extra_settings JSONB        NULL,                   -- 추가 설정(JSON)
  created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 임베딩용 시스템 키 (문서 업로드/컬렉션에서 선택하는 키)
INSERT INTO model_api_key
(alias, provider_code, model, endpoint_url, usage_code, api_key, is_public, is_enabled, extra_settings)
VALUES
('system-openai-embed', 'openai', 'system-openai-embed',
 'https://api.openai.com', 'embed',
 'sk-demo-embed-xxxxxxxxxxxxxxxxxxxx',
 FALSE, TRUE, '{"note": "system default embed key"}')
ON CONFLICT DO NOTHING;

-- 스크린샷에 나온 TEST_API_Key
INSERT INTO model_api_key
(alias, provider_code, model, endpoint_url, usage_code, api_key, is_public, is_enabled, extra_settings)
VALUES
('TEST_API_Key', 'openai', 'gpt-5-nano',
 'https://api.example.com', 'chat',
 'sk-demo-test-xxxxxxxxxxxxxxxxxxxx',
 FALSE, TRUE, '{"region":"us-east-1"}')
ON CONFLICT DO NOTHING;


-- === 2) MCP 서버 테이블 =============================================
-- UI: "MCP 서버 생성" 팝업 대응
CREATE TABLE IF NOT EXISTS mcp_server (
  id         BIGSERIAL PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,  -- 이름 (예: mcp-rag-server)
  description TEXT,
  transport  VARCHAR(10)  NOT NULL,  -- http / https
  url        VARCHAR(255) NOT NULL,  -- 예: http://host:8080
  headers    JSONB        NULL,      -- 예: { "X-Internal-Token": "*******" }
  is_enabled BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP    NOT NULL DEFAULT NOW()
);

INSERT INTO mcp_server
(name, description, transport, url, headers, is_enabled)
VALUES
('mcp-rag-server',
 'RAG용 내부 검색 MCP 서버 (발표용 더미 데이터)',
 'http',
 'http://host:8080',
 '{"X-Internal-Token": "*******"}',
 TRUE)
ON CONFLICT DO NOTHING;


-- === 3) 컬렉션 테이블 ===============================================
-- UI: "새 컬렉션 생성" 팝업 대응
CREATE TABLE IF NOT EXISTS kb_collection (
  id          BIGSERIAL PRIMARY KEY,
  name        VARCHAR(255) NOT NULL,   -- 컬렉션 이름
  description TEXT,
  model_key_id BIGINT NOT NULL,        -- 모델 키 선택 (FK처럼 사용)
  is_public   BOOLEAN NOT NULL DEFAULT FALSE, -- 공개 컬렉션 체크박스
  created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_kb_collection_model_key
    FOREIGN KEY (model_key_id) REFERENCES model_api_key(id)
);

-- system-openai-embed 키를 쓰는 데모 컬렉션
INSERT INTO kb_collection
(name, description, model_key_id, is_public)
VALUES
(
  'demo-rag-collection',
  '발표용 RAG 데모 컬렉션',
  (SELECT id FROM model_api_key WHERE alias = 'system-openai-embed' LIMIT 1),
  TRUE
)
ON CONFLICT DO NOTHING;


-- === 4) 문서 업로드 Job 테이블 ======================================
-- UI: "문서 업로드" 팝업 대응
CREATE TABLE IF NOT EXISTS kb_upload_job (
  id            BIGSERIAL PRIMARY KEY,
  collection_id BIGINT    NOT NULL,  -- 어느 컬렉션에 업로드했는지
  original_name VARCHAR(255),
  chunk_size    INT       NOT NULL,  -- 청크 크기
  chunk_overlap INT       NOT NULL,  -- 청크 오버랩
  model_key_id  BIGINT    NOT NULL,  -- 모델 키 선택
  metadata      JSONB,
  status        VARCHAR(20) NOT NULL DEFAULT 'pending',
  created_at    TIMESTAMP   NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_kb_upload_job_collection
    FOREIGN KEY (collection_id) REFERENCES kb_collection(id),
  CONSTRAINT fk_kb_upload_job_model_key
    FOREIGN KEY (model_key_id)   REFERENCES model_api_key(id)
);

-- 스크린샷 값 그대로: 청크 1000 / 오버랩 200 / 메타데이터 {"key":"value"}
INSERT INTO kb_upload_job
(collection_id, original_name, chunk_size, chunk_overlap, model_key_id, metadata, status)
VALUES
(
  (SELECT id FROM kb_collection WHERE name = 'demo-rag-collection' LIMIT 1),
  'demo_guide.pdf',
  1000,
  200,
  (SELECT id FROM model_api_key WHERE alias = 'system-openai-embed' LIMIT 1),
  '{"key": "value"}',
  'completed'
);
