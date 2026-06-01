import { AlertCircle } from 'lucide-react';
import { ButtonLink } from '../common/Button';

const messages = {
  ocr_failed: {
    title: '텍스트를 읽어내지 못했어요',
    description: '스캔이 흐리거나 손글씨가 많은 경우 인식이 어려울 수 있어요. 더 선명한 파일로 다시 시도해 주세요.',
  },
  not_contract: {
    title: '계약서로 보이지 않아요',
    description: '전월세·임대차 계약서를 올려 주세요. 다른 문서는 아직 분석할 수 없어요.',
  },
  unsupported_format: {
    title: '지원하지 않는 형식이에요',
    description: 'PDF, JPG, PNG 파일만 업로드할 수 있어요.',
  },
  rate_limited: {
    title: '요청이 많아 잠시 지연되고 있어요',
    description: '분석 요청이 한꺼번에 몰렸어요. 1~2분 후 같은 파일로 다시 시도해 주세요.',
  },
  analysis_failed: {
    title: '분석에 실패했어요',
    description: '잠시 후 다시 시도해 주세요. 같은 문제가 반복되면 파일을 바꿔서 올려 주세요.',
  },
};

export default function ErrorMessage({ code }: { code: string | null }) {
  const message = messages[code as keyof typeof messages] ?? messages.analysis_failed;

  return (
    <div className="mx-auto flex max-w-xl flex-col items-center text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-brand">
        <AlertCircle size={34} aria-hidden="true" />
      </div>
      <p className="mt-5 text-sm font-bold text-brand-accent">HERO 분석 안내</p>
      <h1 className="mt-2 text-2xl font-bold text-brand">{message.title}</h1>
      <p className="mt-3 break-keep text-sm leading-6 text-brand-muted">{message.description}</p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <ButtonLink to="/" variant="primary">
          다시 시도하기
        </ButtonLink>
        <ButtonLink to="/" variant="ghost">
          처음으로
        </ButtonLink>
      </div>
    </div>
  );
}
